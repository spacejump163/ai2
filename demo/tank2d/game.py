# -*- encoding: utf-8 -*-
import math
import sys

from PyQt5.QtCore import QTimer, QRectF, QPointF
from PyQt5.QtGui import QBitmap, QPainterPath, QColor, QPainter
from PyQt5.QtWidgets import \
    QGraphicsView, QGraphicsItem, QApplication, QGraphicsScene, QGraphicsItemGroup

UNIT = 20.0


class CannonGraphics(QGraphicsItem):
    BODY = QRectF(-2.0 * UNIT, -2.0 * UNIT, 4.0 * UNIT, 4.0 * UNIT)
    HEAD = QRectF(-0.75 * UNIT, -0.75 * UNIT, 1.5 * UNIT, 1.5 * UNIT)
    CANNON = QRectF(-0.2 * UNIT, 0.5 * UNIT, 0.4 * UNIT, 1.5 * UNIT)
    def __init__(self, color):
        super(CannonGraphics, self).__init__()
        self.body_color = color

    def shape(self):
        p = QPainterPath()
        p.addRect(self.BODY)
        return p

    def boundingRect(self):
        return self.BODY

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.body_color)
        painter.drawRect(self.CANNON)
        painter.drawEllipse(self.HEAD)


class TankGraphics(QGraphicsItem):
    BODY = QRectF(-1 * UNIT, -2 * UNIT, 2 * UNIT, 4 * UNIT)
    REAR_BODY = QRectF(-1 * 0.9 * UNIT, -2 * 0.9 * UNIT, 2 * 0.9 * UNIT, 1 * 0.9 * UNIT)
    def __init__(self, color):
        super(TankGraphics, self).__init__()
        self.body_color = color

    def shape(self):
        p = QPainterPath()
        p.addRect(self.BODY)
        return p

    def boundingRect(self):
        return self.BODY

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.body_color)
        painter.drawRect(self.BODY)
        painter.drawRect(self.REAR_BODY)


class MissileGraphics(QGraphicsItem):
    BODY = QRectF(-0.2 * UNIT, -0.5 * UNIT, 0.2 * UNIT, 1.0 * UNIT)
    def __init__(self, color):
        super(MissileGraphics, self).__init__()
        self.body_color = color

    def shape(self):
        p = QPainterPath()
        p.addRect(self.BODY)
        return p

    def boundingRect(self):
        return self.BODY

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.body_color)
        painter.drawRect(self.BODY)


class GameObject(object):
    def __init__(self):
        self.alive = True
        self.arena = None
        self.position = QPointF()
        self.rotation = 0
        self.move_speed = 0
        self.rotate_speed = 0
        self.graphics = None
        self.group = -1
        self.age = 0

    def start(self):
        pass

    def move_forward(self, v):
        self.move_speed = v

    def rotate_clockwise(self, w):
        self.rotate_speed = w

    def update(self):
        self.update_logic()
        self.update_graphics()

    def update_logic(self):
        dv = QPointF(math.cos(self.rotation), math.sin(self.rotation))
        dv *= self.move_speed * self.arena.dt
        self.position += dv
        self.rotation += self.rotate_speed * self.arena.dt
        self.age += self.arena.dt

    def update_graphics(self):
        a = math.degrees(self.rotation) - 90
        self.graphics.setRotation(a)
        self.graphics.setPos(self.position)

    def cleanup(self):
        self.alive = False


class Tank(GameObject):
    FIRE_CD = 1.0
    MAX_MOVE_SPEED = UNIT * 8
    MAX_CANNON_ROTATION_SPEED = math.pi / 1.0
    MAX_BODY_ROTATION_SPEED = math.pi / 2.0

    def __init__(self, color, group):
        super(Tank, self).__init__()
        self.graphics = QGraphicsItemGroup()
        self.body_graphics = TankGraphics(color)
        self.graphics.addToGroup(self.body_graphics)
        self.cannon_graphics = CannonGraphics(color)
        self.graphics.addToGroup(self.cannon_graphics)

        self.cannon_rotation = 0
        self.cannon_rotate_speed = 0
        self.group = group
        self.hp = 100

        self.fire_cd = 0

    def start(self):
        self.move_forward(10)

    def update_logic(self):
        super(Tank, self).update_logic()
        self.cannon_rotation += self.cannon_rotate_speed * self.arena.dt
        self.fire_cd -= self.arena.dt

    def update_graphics(self):
        super(Tank, self).update_graphics()
        a = math.degrees(self.cannon_rotation)
        self.cannon_graphics.setRotation(a)

    def get_world_aiming(self):
        return self.rotation + self.cannon_rotation

    def adjust_aim_clockwise(self, w):
        self.cannon_rotate_speed = w

    def open_fire(self):
        if self.fire_cd <= 0:
            self.fire_cd = self.FIRE_CD
            orient = self.get_world_aiming()
            dv = QPointF(math.cos(orient), math.sin(orient)) * 2.5 * UNIT
            pos = self.position + dv
            m = Missile(pos, orient, 10 * UNIT)
            self.arena.add(m)
            return True
        else:
            return False

    def update(self):
        super(Tank, self).update()

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.cleanup()


class Missile(GameObject):
    def __init__(self, pos, orient, speed, color = QColor(255, 0, 0, 255)):
        super(Missile, self).__init__()
        self.graphics = MissileGraphics(color)
        self.position = pos
        self.rotation = orient
        self.move_speed = speed
        self.ttl = 1
        self.damage = 10

    def update(self):
        super(Missile, self).update()
        self.ttl -= self.arena.dt
        if self.ttl < 0:
            self.cleanup()
        else:
            self.check_explode()

    def check_explode(self):
        targets = self.arena.get_enemies_in_range(self, UNIT * 2)
        if len(targets) == 0:
            return
        for t in targets:
            if hasattr(t, "take_damage"):
                t.take_damage(self.damage)
        self.cleanup()


class TankAgent(Tank):
    def __init__(self, color, group):
        super(TankAgent, self).__init__(color, group)
        self.target = None

    @staticmethod
    def get_shortest_angle_path(a):
        rounds = 1.0 * a / (2 * math.pi)
        if rounds > 0:
            rounds = rounds - int(rounds)
        if rounds > 0.5:
            rounds -= 1.0
        elif rounds < -0.5:
            rounds += 1.0
        return rounds * 2 * math.pi

    def get_shortest_cannon_angle_path_towards(self, target):
        dv = target.position - self.position
        dest_angle = math.atan2(dv.y(), dv.x())
        current_angle = self.get_world_aiming()
        da = dest_angle - current_angle
        a = self.get_shortest_angle_path(da)
        return a

    def get_shortest_body_angle_path_towards(self, target):
        dv = target.position - self.position
        dest_angle = math.atan2(dv.y(), dv.x())
        current_angle = self.rotation
        da = dest_angle - current_angle
        a = self.get_shortest_angle_path(da)
        return a

    def aim_cannon_towards_tick(self, target):
        a = self.get_shortest_cannon_angle_path_towards(target)
        if math.fabs(a) < self.MAX_CANNON_ROTATION_SPEED * self.arena.dt:
            self.cannon_rotate_speed = 0
        elif a > 0:
            self.cannon_rotate_speed = self.MAX_CANNON_ROTATION_SPEED
        else:
            self.cannon_rotate_speed = -self.MAX_CANNON_ROTATION_SPEED

    def aim_body_towards_tick(self, target, offset):
        a = self.get_shortest_body_angle_path_towards(target) + offset
        if math.fabs(a) < self.MAX_BODY_ROTATION_SPEED * self.arena.dt:
            self.rotate_speed = 0
        elif a > 0:
            self.rotate_speed = self.MAX_BODY_ROTATION_SPEED
        else:
            self.rotate_speed = -self.MAX_BODY_ROTATION_SPEED

    def update(self):
        super(TankAgent, self).update()


def get_cstep(a, b):
    def cstep(x):
        x2 = x ** 2
        if x >= 0:
            return 1.0 * b * x2 / (a + x2)
        else:
            return -1.0 * b * x2 / (a + x2)


class RounderTank(TankAgent):
    def update(self):
        super(TankAgent, self).update()
        if self.target is not None:
            d = (self.target.position - self.position)
            dx = d.x()
            dy = d.y()
            d = (dx ** 2 + dy ** 2) ** 0.5
            #if d > TODO:hererere
            self.aim_cannon_towards_tick(self.target)
            self.aim_body_towards_tick(self.target, math.pi / 2)
            if self.age > 3.0:
                self.move_speed = self.MAX_MOVE_SPEED * 0.2


class Arena(object):
    FPS = 33.0
    GAME_PERIOD = 1.0 / FPS
    def __init__(self):
        self.children = []
        self.new_children = []
        self.clock = None
        self.time = 0
        self.dt = self.GAME_PERIOD

    def start(self):
        if self.clock is None:
            self.clock = QTimer()
            self.clock.timeout.connect(self.update)
            self.clock.start(1000.0 / self.FPS)

    def pause(self):
        self.clock.stop()
        self.clock = None

    def add(self, obj):
        self.new_children.append(obj)
        obj.arena = self
        assert(obj.graphics is not None)
        obj.update_graphics()
        self.scene.addItem(obj.graphics)

    def update(self):
        for c in self.children:
            if c.alive:
                c.update()
        for c in self.children:
            if c.alive:
                self.new_children.append(c)
            else:
                self.scene.removeItem(c.graphics)
        self.children = self.new_children
        self.new_children = []

    def set_scene(self, scene):
        self.scene = scene

    def get_enemies_in_range(self, obj, radius):
        enemies = []
        group = obj.group
        point = obj.position
        for c in self.children:
            if c.alive and c.group != group:
                dv = c.position - point
                x = dv.x()
                y = dv.y()
                r = math.sqrt(x * x + y * y)
                if r < radius:
                    enemies.append(c)
        return enemies


class App(object):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.init_scene()
        self.init_game()

    def init_scene(self):
        self.scene = QGraphicsScene()
        scene = self.scene
        scene.setSceneRect(-1920 / 2, -1080 / 2, 1920, 1080)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)

        view = self.view = QGraphicsView(scene)
        view.setGeometry(100, 100, 800, 800)
        view.setRenderHint(QPainter.Antialiasing)
        #view.setBackgroundBrush(QBrush(QColor(0, 255, 0), Qt.CrossPattern))
        view.setCacheMode(QGraphicsView.CacheBackground)
        view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        view.show()

    def init_game(self):
        self.init_arena()
        self.init_players()
        self.arena.start()

    def init_arena(self):
        self.arena = Arena()
        self.arena.set_scene(self.scene)

    def init_players(self):
        tank0 = RounderTank(QColor(0, 255, 0, 255), 1)
        tank0.position = QPointF(UNIT * 10, UNIT * 10)
        tank0.rotation = math.pi / 180 * 45
        tank0.cannon_rotation = math.pi / 180 * 45
        self.arena.add(tank0)

        tank1 = TankAgent(QColor(0, 255, 255, 255), 2)
        tank1.position = QPointF(0, 0)
        self.arena.add(tank1)

        tank0.target = tank1


    def old_init(self):
        tank0 = Tank(QColor(0, 255, 0, 255), 1)
        tank0.position = QPointF(0, UNIT * 10)
        tank0.rotation = math.pi * 3 / 2
        tank0.hp = 20
        #tank.adjust_aim_clockwise(math.pi / 2)
        self.arena.add(tank0)

        tank1 = Tank(QColor(0, 255, 255, 255), 2)
        tank1.position = QPointF(0, 0)
        tank1.rotation = math.pi / 2
        #tank.adjust_aim_clockwise(math.pi / 2)
        self.arena.add(tank1)

    def run(self):
        self.app.exec_()

    def update(self):
        self.arena.update()


def run_game():
    app = App()
    app.run()

if __name__ == "__main__":
    run_game()