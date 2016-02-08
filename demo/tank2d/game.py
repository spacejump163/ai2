# -*- encoding: utf-8 -*-
import math
import random
import sys
import logging

from PyQt5.QtCore import QTimer, QRectF, QPointF, Qt
from PyQt5.QtGui import QBitmap, QPainterPath, QColor, QPainter
from PyQt5.QtWidgets import \
    QGraphicsView, QGraphicsItem, QApplication, QGraphicsScene, QGraphicsItemGroup

from ai2.runtime.debug_stub import DebugStub

from ai2.runtime import loader
loader.prefix = "ai_data."


UNIT = 80.0

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CannonGraphics(QGraphicsItem):
    BODY = QRectF(-0.5 * UNIT, -0.5 * UNIT, 1.0 * UNIT, 1.0 * UNIT)
    HEAD = QRectF(-0.75 * UNIT / 4, -0.75 * UNIT / 4, 1.5 * UNIT / 4, 1.5 * UNIT / 4)
    CANNON = QRectF(-0.2 * UNIT / 4, 0.5 * UNIT / 4, 0.4 * UNIT / 4, 1.5 * UNIT / 4)
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
    BODY = QRectF(-1 * UNIT / 4, -2 * UNIT / 4, 2 * UNIT / 4, 4 * UNIT / 4)
    REAR_BODY = QRectF(-1 * 0.9 * UNIT / 4, -2 * 0.9 * UNIT / 4, 2 * 0.9 * UNIT / 4, 1 * 0.9 * UNIT / 4)
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
    BODY = QRectF(-0.2 * UNIT / 4, -0.5 * UNIT / 4, 0.2 * UNIT / 4, 1.0 * UNIT / 4)
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
        self.new = False
        self.alive = True
        self.arena = None
        self.position = QPointF()
        self._rotation = 0
        self.move_speed = 0
        self.rotate_speed = 0
        self.graphics = None
        self.group = -1
        self.age = 0

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

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, v):
        self._rotation = self.get_shortest_angle_path(v)

    def start(self):
        pass

    def move_forward(self, v):
        self.move_speed = v

    def rotate_clockwise(self, w):
        self.rotate_speed = w

    def update(self):
        if self.new:
            self.start()
            self.new = False
            self.new = False
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
    MAX_MOVE_SPEED = UNIT * 2
    MAX_CANNON_ROTATION_SPEED = math.pi / 1.0
    MAX_BODY_ROTATION_SPEED = math.pi / 4.0
    MISSILE_SPEED = 2.5 * UNIT

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
        self.hp = 50

        self.fire_cd = 0

    def start(self):
        pass

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
            dv = QPointF(math.cos(orient), math.sin(orient)) * 0.6 * UNIT
            pos = self.position + dv
            m = Missile(pos, orient, self.MISSILE_SPEED)
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
        self.ttl = 5
        self.damage = 10

    def update(self):
        super(Missile, self).update()
        self.ttl -= self.arena.dt
        if self.ttl < 0:
            self.cleanup()
        else:
            self.check_explode()

    def check_explode(self):
        targets = self.arena.get_enemies_in_range(self, 0.5)
        if len(targets) == 0:
            return
        for t in targets:
            if hasattr(t, "take_damage"):
                t.take_damage(self.damage)
        self.cleanup()


class AITank(Tank):
    def __init__(self, color, group):
        self.target = None
        super(AITank, self).__init__(color, group)

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
        if math.fabs(a) < self.MAX_BODY_ROTATION_SPEED * self.arena.dt / 2:
            self.rotate_speed = 0
        elif a > 0:
            self.rotate_speed = self.MAX_BODY_ROTATION_SPEED
        else:
            self.rotate_speed = -self.MAX_BODY_ROTATION_SPEED

    def move_around_tick(self, target, near, far, speed_percent):
        slope_func = get_slope_function(near, far)
        dv = target.position - self.position
        dx = dv.x()
        dy = dv.y()
        d = (dx ** 2 + dy ** 2) ** 0.5
        a = slope_func(d)
        speed_func = lambda x: 1 - (x ** 2) / (math.pi ** 2)
        self.aim_body_towards_tick(target, a)
        self.move_speed = \
            self.MAX_MOVE_SPEED * speed_percent * speed_func(a)

    def estimated_aim_tick(self, target):
        estimated_fake_target = self.get_estimated_position(target)
        a = self.get_shortest_cannon_angle_path_towards(estimated_fake_target)
        if math.fabs(a) < self.MAX_CANNON_ROTATION_SPEED * self.arena.dt:
            self.cannon_rotate_speed = 0
        elif a > 0:
            self.cannon_rotate_speed = self.MAX_CANNON_ROTATION_SPEED
        else:
            self.cannon_rotate_speed = -self.MAX_CANNON_ROTATION_SPEED

    def get_estimated_position(self, target):
        dv = target.position - self.position
        targetv = QPointF(
            math.cos(target.rotation),
            math.sin(target.rotation)) * self.move_speed
        dvl = ((dv.x() ** 2) + (dv.y() ** 2)) ** 0.5
        t = dvl / self.MISSILE_SPEED
        if t < 2:
            t = 2
        epos = target.position + targetv * (t * random.uniform(1.0, 3.0))
        return tank_agent.FakeTarget(epos)

    def update(self):
        super(AITank, self).update()


def get_slope_function(a, b):
    def func(x):
        if x < a:
            return math.pi
        elif x < b:
            return (b - x) * math.pi / (b - a)
        else:
            return 0
    return func

func100_200 = get_slope_function(3 * UNIT, 4 * UNIT)


class RounderAITank(AITank):
    def go_round_tick(self):
        if self.target is not None:
            d = (self.target.position - self.position)
            dx = d.x()
            dy = d.y()
            d = (dx ** 2 + dy ** 2) ** 0.5
            self.aim_cannon_towards_tick(self.target)
            a = func100_200(d)
            self.aim_body_towards_tick(self.target, a)
            if self.age > 3.0:
                self.move_speed = self.MAX_MOVE_SPEED * 1

    def search_enemy_tick(self):
        if self.target and self.target.alive is False:
            self.target = None

        if self.target is None:
            enemies = self.arena.get_enemies_in_range(self, 20)
            if enemies:
                self.target = enemies[0]

    def fire_tick(self):
        if self.target:
            self.open_fire()

    def update(self):
        super(RounderAITank, self).update()
        self.search_enemy_tick()
        self.go_round_tick()
        #self.fire_tick()


import tank_agent


class TimerObject(object):
    def __init__(self, interval, callback, times):
        self.times = times
        self.callback = callback
        self._timer = QTimer()
        #logger.info("register timer %s" % self)
        self._timer.timeout.connect(self.expired)
        self._timer.start(interval * 1000)

    def expired(self):
        #logger.info("callback from %s" % self)
        self.callback()
        self.times -= 1
        if self._timer is None:
            #logger.info("dead timer %s called, ignore" % self)
            return
        if self.times == 0:
            self._timer.stop()
            #logger.info("delete timer %s" % self)
            self._timer = None

    def cancel(self):
        #logger.info("cancel timer %s" % self)
        if self._timer:
            self._timer.stop()
            self._timer = None


class AI2AITank(AITank):
    def __init__(self, color, group):
        self._ticks = set()
        super(AI2AITank, self).__init__(color, group)

    def take_damage(self, dmg):
        super(AI2AITank, self).take_damage(dmg)
        self.agent.fire_event("damaged")

    def start(self):
        self.agent = tank_agent.TankAgent(self)
        self.agent.blackboard["disabled_tree"] = "disabled_btree"
        self.agent.blackboard["normal_tree"] = "walk_around_shooter_btree"
        self.agent.start("simple_tank_fsm")

    def add_timer(self, interval, callback, times):
        return TimerObject(interval, callback, times)

    def update(self):
        super(AI2AITank, self).update()
        copied_ticks = set(self._ticks)
        for tick in copied_ticks:
            tick()

    def add_tick(self, tick):
        self._ticks.add(tick)

    def remove_tick(self, tick):
        self._ticks.remove(tick)


class Arena(object):
    FPS = 33.0
    GAME_PERIOD = 1.0 / FPS
    def __init__(self):
        self.children = []
        self.new_children = []
        self.clock = None
        self.time = 0
        self.dt = 1.0 / self.FPS

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
            if c.alive and c.group != group and not isinstance(c, Missile):
                dv = c.position - point
                x = dv.x()
                y = dv.y()
                r = math.sqrt(x * x + y * y)
                if r < radius * UNIT:
                    enemies.append(c)
        return enemies

    def get_bullets_in_range(self, pos, radius):
        bullets = []
        for c in self.children:
            if c.alive and isinstance(c, Missile):
                dv = c.position - pos
                x = dv.x()
                y = dv.y()
                r = math.sqrt(x * x + y * y)
                if r < radius * UNIT:
                    bullets.append(c)
        return bullets


class App(object):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.init_scene()
        self.debug_stub = DebugStub(8000)
        self.debug_stub.run()
        self.init_game()
        self.arena.start()
        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.check_and_spawn_tick)
        self.spawn_timer.start(2000)

    def init_scene(self):
        self.scene = QGraphicsScene()
        scene = self.scene
        scene.setSceneRect(-10 * UNIT, -10 * UNIT, 20 * UNIT, 20 * UNIT)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)

        view = self.view = QGraphicsView(scene)
        view.setGeometry(100, 100, 15 * UNIT, 15 * UNIT)
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
        tank1 = AI2AITank(Qt.blue, 2)
        tank1.position = QPointF(UNIT * 0, UNIT * 0)
        self.arena.add(tank1)
        tank1.start()
        tank1.agent.debug_id = "tank1"
        self.debug_stub.add_agent(tank1.agent)

        self.spawn_tank_in_range((0, 0), 4)

    def spawn_tank_in_range(self, pos, radius):
        tank = RounderAITank(Qt.red, 1)
        if isinstance(pos, tuple):
            tank.position = QPointF(pos[0] * UNIT, pos[1] * UNIT)
        else:
            tank.position = pos
        ra = random.uniform(0, math.pi * 2)
        d = random.uniform(radius * 0.5 * UNIT, radius * UNIT)
        tank.position += QPointF(math.cos(ra), math.sin(ra)) * d
        tank.rotation = ra
        tank.cannon_rotation = 0
        self.arena.add(tank)

    def run(self):
        self.app.exec_()

    @property
    def n_player(self):
        acc = 0
        for i in self.arena.children:
            if i.alive and isinstance(i, Tank):
                acc += 1
        return acc

    def check_and_spawn_tick(self):
        if self.n_player < 3:
            self.spawn_tank_in_range((0, 0), 8)

    def update(self):
        self.arena.update()

    def stop(self):
        self.debug_stub.stop()
        print("shutdown over")

PLAYER_CONFIGS = (
    (Tank, Qt.green, 1),
    (AITank, Qt.yellow, 2),
    #(Qt.red, 3),
    #(Qt.blue, 4),
)

def run_game():
    logger.addHandler(logging.StreamHandler())
    logger.info("game start:")
    app = App()
    app.run()
    app.stop()

if __name__ == "__main__":
    run_game()