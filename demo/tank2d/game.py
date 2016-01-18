# -*- encoding: utf-8 -*-
import math
import sys

from PyQt5.QtCore import QTimer, QRectF, QPointF
from PyQt5.QtGui import QBitmap, QPainterPath, QColor, QPainter
from PyQt5.QtWidgets import \
    QGraphicsView, QGraphicsItem, QApplication, QGraphicsScene, QGraphicsItemGroup

UNIT = 20.0


class CannonGraphics(QGraphicsItem):
    BODY = QRectF(-0.75 * UNIT, -0.75 * UNIT, 1.5 * UNIT, 2.0 * UNIT)
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
        self.orientation = 0
        self.move_speed = 0
        self.rotate_speed = 0
        self.graphics = None

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
        dv = QPointF(math.cos(self.orientation), math.sin(self.orientation))
        dv *= self.move_speed
        self.position += dv
        self.orientation += self.rotate_speed

    def update_graphics(self):
        a = math.degrees(self.orientation) - 90
        self.graphics.setRotation(a)
        self.graphics.setPos(self.position)

    def cleanup(self):
        self.alive = False


class Tank(GameObject):
    def __init__(self):
        super(Tank, self).__init__()
        self.graphics = QGraphicsItemGroup()
        self.body_graphics = TankGraphics()
        self.graphics.addToGroup(self.body_graphics)
        self.cannon_graphics = CannonGraphics()
        self.graphics.addToGroup(self.cannon_graphics)

        self.cannon_rotation = 0
        self.cannon_rotation_speed = 0

    def start(self):
        self.move_forward(10)

    def update(self):
        pass

    def cleanup(self):
        pass

    def adjust_aim_clockwise(self, w):
        pass

    def action_fire(self):
        pass


class Missile(GameObject):
    def __init__(self, pos, orient, speed, color = QColor(255, 0, 0, 255)):
        super(Missile, self).__init__()
        self.graphics = MissileGraphics(color)
        self.position = pos
        self.orientation = orient
        self.move_speed = speed


class Arena(object):
    GAME_PERIOD = 1000.0 / 33
    def __init__(self):
        self.children = []
        self.new_children = []
        self.clock = None
        self.time = 0

    def start(self):
        if self.clock is None:
            self.clock = QTimer()
            self.clock.timeout.connect(self.update)
            self.clock.start(self.GAME_PERIOD)

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
        self.children = self.new_children
        self.new_children = []

    def set_scene(self, scene):
        self.scene = scene

class App(object):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.init_scene()
        self.init_game()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def init_scene(self):
        self.scene = QGraphicsScene()
        scene = self.scene
        scene.setSceneRect(-1920 / 2, -1080 / 2, 1920, 1080)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)

        view = self.view = QGraphicsView(scene)
        view.setGeometry(100, 100, 800, 600)
        view.setRenderHint(QPainter.Antialiasing)
        #view.setBackgroundBrush(QBrush(QColor(0, 255, 0), Qt.CrossPattern))
        view.setCacheMode(QGraphicsView.CacheBackground)
        view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        view.show()

    def init_game(self):
        self.arena = Arena()
        self.arena.set_scene(self.scene)
        missle = Missile(QPointF(0, 0), 0, 10)
        self.arena.add(missle)

    def run(self):
        self.app.exec_()

    def update(self):
        self.arena.update()


if __name__ == "__main__":
    app = App()
    app.run()