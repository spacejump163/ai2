# -*- encoding: utf-8 -*-
import sys

from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsItem, \
    QGraphicsItemGroup, QGraphicsSimpleTextItem
from PyQt5.QtCore import QRectF, Qt, QPointF, QTimer, QPoint, QLineF
from PyQt5.QtGui import QPainterPath, QTransform, QColor, QBrush, QPainter

import ai2.tools.btree_editor.model as model

UNIT = 10

"""
class TestWindow(QMainWindow):
    def __init__(self):
        super(TestWindow, self).__init__()
        self.init_graphics()
        self.init_debug_traits()
        self.init_elements_save()

    def init_graphics(self):
        self.scene = QGraphicsScene()
        self.view = NodeEditorView(self.scene)
        self.view.update_handler = self.update_handler
        self.scene.setSceneRect(QRectF(-UNIT * 100, -UNIT * 100, UNIT * 200, UNIT * 200))
        self.setCentralWidget(self.view)

    def update_handler(self):
        m = model.build_test_tree_model()
        self.cleanup()
        self.init_debug_traits()
        self.display_tree_model(m)

    def display_tree_model(self, model):
        root = self.build_tree(model.root)
        layouter = TreeNodeLayouter(root)
        layouter.run()
        self.display_links_rec(root)

    def display_links_rec(self, cur):
        spos = cur.right_pos()
        for c in cur.children:
            dpos = c.left_pos()
            self.scene.addLine(QLineF(spos, dpos))
            self.display_links_rec(c)

    def build_tree(self, node):
        chs = []
        for c in node.children:
            t = self.build_tree(c)
            chs.append(t)
        n = self.build_node_from_model(node)
        n.children = chs
        return n

    def build_node_from_model(self, model):
        name = model.get_display_text()
        #name = model.get_name()
        n = BasicNode(name, model)
        self.scene.addItem(n)
        return n

    def init_debug_traits(self):
        center = self.scene.addRect(QRectF(-20, -20, 40, 40))

    def cleanup(self):
        self.scene.clear()

    def init_elements_save(self):
        center = self.scene.addRect(QRectF(-20, -20, 40, 40))

        n0 = BasicNode("n0")
        n0.setPos(0, 0)
        self.scene.addItem(n0)

        n00 = BasicNode("n00")
        n00.setPos(100, 100)
        self.scene.addItem(n00)

        n01 = BasicNode("n01")
        n01.setPos(100, 0)
        self.scene.addItem(n01)

        n000 = BasicNode("n000")
        n000.setPos(200, 200)
        self.scene.addItem(n000)

        n001 = BasicNode("n001")
        n001.setPos(200, 100)
        self.scene.addItem(n001)

        n010 = BasicNode("n010")
        n010.setPos(200, 0)
        self.scene.addItem(n010)

        self.view.centerOn(center)

    def closeEvent(self, *args, **kwargs):
        sys.exit(0)
"""

class NodeEditorView(QGraphicsView):
    def __init__(self, *args):
        super(NodeEditorView, self).__init__(*args)
        self.setRenderHints(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, e):
        STEP = 1.2
        d = e.angleDelta()
        if d.y() > 0:
            self.scale(STEP, STEP)
        elif d.y() < 0:
            self.scale(1 / STEP, 1 / STEP)
        else:
            assert(False)
        self.current_transform = self.transform()

    def keyPressEvent(self, ev):
        k = ev.key()
        if k == Qt.Key_1:
            self.update_handler()
        return super(NodeEditorView, self).keyPressEvent(ev)


class BoxOutline(QGraphicsItem):
    def __init__(self, bg_color):
        super(BoxOutline, self).__init__()
        self.rect = QRectF()
        self.bg_color = bg_color

    def shape(self):
        path = QPainterPath()
        path.addRect(self.rect)
        return path

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.black)
        painter.setBrush(self.bg_color)
        r = self.rect.height() / 8.0
        painter.drawRoundedRect(self.rect, r, r)


class BasicNode(QGraphicsItemGroup):
    def __init__(self, model, manager, bg_color=Qt.green, text_color=Qt.black):
        super(BasicNode, self).__init__()
        self.model = model
        text = model.get_display_text()
        self.manager = manager
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.text_graph = QGraphicsSimpleTextItem(text)
        self.text_graph.setBrush(text_color)
        bound = self.text_graph.boundingRect()
        r = QPointF(bound.width() / 2, bound.height() / 2)
        text_center = self.text_graph.pos() + r
        self.text_graph.setPos(-text_center)
        self.addToGroup(self.text_graph)

        self.box_graph = BoxOutline(bg_color)
        empty_space = QPointF(UNIT, UNIT)
        newr = (empty_space + r)
        self.box_graph.rect = QRectF(-newr, newr)
        self.addToGroup(self.box_graph)
        self.text_graph.setZValue(1.0)
        self.box_graph.setZValue(0.0)

        self.children = []

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.manager.selection_changed(self, value)
        else:
            pass
        return super(BasicNode, self).itemChange(change, value)

    """
    def boundingRect(self):
        rect = super(BasicNode, self).boundingRect()
        c = rect.center()
        r = QPointF(rect.width() / 2, rect.height() / 2)
        c0 = c - r * 1.2
        c1 = c + r * 1.2
        nrect = QRectF(c0, c1)
        return nrect
    """

    def get_width(self):
        return self.boundingRect().width()

    def setPosLeft(self, pos):
        pos += QPoint(self.get_width() / 2.0, 0)
        self.setPos(pos)

    def left_pos(self):
        return self.pos() - QPointF(self.get_width() / 2.0, 0)

    def center_pos(self):
        return self.pos()

    def right_pos(self):
        return self.pos() + QPointF(self.get_width() / 2.0, 0)

    def contextMenuEvent(self, ev, *args, **kwargs):
        print("context menu event for %s" % (self))

class TreeNodeLayouter(object):
    def __init__(self, root):
        self.widths = []
        self.root = root
        self.next_y = -1
        self.funcx = lambda x: x
        self.funcy = lambda x: x

    def gety(self):
        self.next_y += 1
        return self.next_y

    def run(self):
        self.fix_xy(self.root, 0)
        self.build_pos_func()
        self.layout_node_rec(self.root)

    def fix_xy(self, current, level=0):
        # update width first
        if level == len(self.widths):
            self.widths.append(-1)
        w = current.get_width()
        if w > self.widths[level]:
            self.widths[level] = w
        # layout x
        current.layout_x = level
        # layout y
        if len(current.children) == 0:
            current.layout_y = self.gety()
            return
        for c in current.children:
            self.fix_xy(c, level+1)

        cs = current.children
        current.layout_y = (cs[0].layout_y + cs[-1].layout_y) / 2.0

    def build_pos_func(self):
        self.build_pos_funcx()
        self.build_pos_funcy()

    def build_pos_funcy(self):
        line_space = UNIT * 5
        offset = 0
        fy = lambda y: line_space * y + offset
        offset = -fy(self.root.layout_y)
        self.funcy = fy

    def build_pos_funcx(self):
        f = lambda x: sum(self.widths[:x]) #+ x * 4 * UNIT
        self.funcx = f

    def layout_node_rec(self, node):
        x = self.funcx(node.layout_x)
        y = self.funcy(node.layout_y)
        p = QPointF(x, y)
        node.setPosLeft(p)

        for c in node.children:
            self.layout_node_rec(c)

"""
def run():
    app = QApplication(sys.argv)
    mainWindow = TestWindow()
    mainWindow.setGeometry(100, 100, 800, 600)
    mainWindow.show()
    app.exec_()
"""