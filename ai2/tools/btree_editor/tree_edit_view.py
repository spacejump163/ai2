# -*- encoding: utf-8 -*-
import sys
import os
import copy

from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsItem, \
    QGraphicsItemGroup, QGraphicsSimpleTextItem
from PyQt5.QtCore import QRectF, Qt, QPointF, QTimer, QPoint, QLineF
from PyQt5.QtGui import QPainterPath, QTransform, QColor, QBrush, QPainter, QPen
from PyQt5.uic import loadUi

import ai2.tools.btree_editor.model as model

this_path = os.path.dirname(__file__)
NODE_SELECTION_UI_PATH = os.path.join(
    this_path,
    "../../../res/gui/node_select_dialog.ui")

UNIT = 10


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
    def __init__(self, model, manager, text_color=Qt.black):
        bg_color = model.get_bg_color()
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

    def get_width(self):
        return self.boundingRect().width()

    def set_left_pos(self, pos):
        pos += QPoint(self.get_width() / 2.0, 0)
        self.setPos(pos)

    def left_pos(self):
        return self.pos() - QPointF(self.get_width() / 2.0, 0)

    def center_pos(self):
        return self.pos()

    def right_pos(self):
        return self.pos() + QPointF(self.get_width() / 2.0, 0)

    """
    def contextMenuEvent(self, ev, *args, **kwargs):
        print("context menu event for %s" % (self))
    """


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
        f = lambda x: sum(self.widths[:x]) + x * 4 * UNIT
        self.funcx = f

    def layout_node_rec(self, node):
        x = self.funcx(node.layout_x)
        y = self.funcy(node.layout_y)
        p = QPointF(x, y)
        node.set_left_pos(p)

        for c in node.children:
            self.layout_node_rec(c)


class NodeEditorVM(object):
    def __init__(self, model, view, scene, parent_vm):
        self.view = view
        self.scene = scene
        self.model = model
        self.parent_vm = parent_vm
        self.selected_node = None
        self.selected_effect = None
        self.graphics_root = None

    ###########################################################################
    # display refresh related
    ###########################################################################
    def display_tree_model(self):
        self.graphics_root = root = self.build_tree(self.model.root)
        layouter = TreeNodeLayouter(root)
        layouter.run()
        self.display_links_rec(root)

    def display_links_rec(self, cur):
        spos = cur.right_pos()
        for c in cur.children:
            dpos = c.left_pos()
            l = self.scene.addLine(QLineF(spos, dpos))
            l.setZValue(1.0)
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
        n = BasicNode(model, self)
        self.scene.addItem(n)
        return n

    def find_graphics_for_node(self, model):
        return self.search_func(self.graphics_root, model)

    def search_func(self, root, model):
        if root.model is model:
            return root
        for c in root.children:
            r = self.search_func(c, model)
            if r:
                return r
        return None

    def refresh(self):
        self.parent_vm.set_dirty()
        self.clean_selection_effect()
        self.scene.clear()
        self.display_tree_model()
        if self.selected_node is None:
            return
        g = self.find_graphics_for_node(self.selected_node)
        g.setSelected(True)

    ###########################################################################
    # selection related
    ###########################################################################
    def cancel_selection(self):
        if self.selected_node is None:
            return
        cnode = self.find_graphics_for_node(self.selected_node)
        cnode.setSelected(False)

    def selection_changed(self, graphics_node, state):
        if state == 0:
            self.selected_node = None
            self.clean_selection_effect()
        else:
            self.selected_node = graphics_node.model
            self.show_selection_effect()

    @staticmethod
    def enlarge_rect(rect):
        offsetx = 2
        offsety = 2
        c = rect.center()
        r = QPointF(rect.width() / 2 + offsetx, rect.height() / 2 + offsety)
        return QRectF(c - r, c + r)

    def show_selection_effect(self):
        if self.selected_node is None:
            return
        selection_pen = QPen()
        selection_pen.setWidth(5)
        cnode = self.find_graphics_for_node(self.selected_node)
        rect = cnode.boundingRect()
        self.selected_effect = self.scene.addRect(self.enlarge_rect(rect), selection_pen)
        self.selected_effect.setPos(cnode.pos())
        self.selected_effect.setZValue(0.5)
        self.parent_vm.parent.add_dock_content(self.selected_node.get_editor(self.refresh))

    def clean_selection_effect(self):
        self.parent_vm.parent.clear_dock_contents()
        if self.selected_effect:
            self.scene.removeItem(self.selected_effect)
        self.selected_effect = None

    ###########################################################################
    # graph editing related
    ###########################################################################

    def insert_handler(self):
        if self.selected_node is None:
            return
        dialog = NodeSelectDialog()
        clz = dialog.run()
        if clz is None:
            return
        self.model.add_node(self.selected_node, clz, None)
        self.refresh()

    def delete_handler(self):
        if self.selected_node is None:
            return
        if self.selected_node.parent == None:
            return
        self.model.cut_tree(self.selected_node)
        self.selected_node = None
        self.refresh()

    def copy_handler(self):
        if self.selected_node is None:
            return
        t = self.copy_subtree(self.selected_node)
        return t

    def paste_handler(self, fragment):
        if self.selected_node is None:
            return
        if fragment is None:
            return
        new_copy = self.copy_subtree(fragment)
        self.model.add_node(self.selected_node, new_copy, None)
        self.refresh()

    def cut_handler(self):
        if self.selected_node is None:
            return
        if self.selected_node.parent == None:
            return
        self.model.cut_tree(self.selected_node)
        fragment = self.selected_node
        self.selected_node = None
        self.refresh()
        return fragment


    @staticmethod
    def copy_subtree(node):
        saved_parent = node.parent
        node.parent = None
        copied = copy.deepcopy(node)
        node.parent = saved_parent
        return copied


class NodeSelectDialog(object):
    def __init__(self):
        classes = self.classes = model.get_all_node_class()
        dialog = loadUi(NODE_SELECTION_UI_PATH)
        self.valid = False
        self.window = dialog
        self.window.list.itemDoubleClicked.connect(self.close_handler)
        for c in classes:
            text = c.type_display_name
            self.window.list.addItem(text)

    def run(self):
        self.window.exec()
        r = self.window.list.currentRow()
        if self.valid:
            return self.classes[r]
        else:
            return None

    def close_handler(self, *args):
        self.valid = True
        self.window.close()