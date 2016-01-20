# -*- encoding: utf-8 -*-
import os
from PyQt5.QtGui import QPen

from PyQt5.QtWidgets import QGraphicsView, QMessageBox, QGraphicsScene
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF

from ai2.tools.btree_editor.tree_edit_view import \
    NodeEditorView, BasicNode, TreeNodeLayouter
from ai2.tools.btree_editor.btree_config import config, UNIT

AREA_WIDTH = 1920 * 2.0
AREA_HEIGHT = 1080 * 2.0
AREA = QRectF(-AREA_WIDTH / 2, -AREA_HEIGHT / 2, AREA_WIDTH, AREA_HEIGHT)


class BTreeInstanceVM(object):
    def __init__(self, model, parent, file_path):
        self.file_path = os.path.abspath(file_path)
        self.modified = False
        self.model = model
        self.parent = parent
        self.current_graphics_node = None
        self.selection_graphics = None

        self.init_view()
        self.sub_window = parent.mdi.addSubWindow(self.btree_view)
        self.sub_window.instance = self
        self.sub_window.setAttribute(Qt.WA_DeleteOnClose)
        self.update_title()
        self.sub_window.closeEvent = self.close_handler
        self.sub_window.show()
        parent.instances.append(self)

        self.refresh()

    def init_view(self):
        self.btree_scene = QGraphicsScene()
        self.btree_view = NodeEditorView(self.btree_scene)
        self.btree_view.setAttribute(Qt.WA_DeleteOnClose)
        self.btree_scene.setSceneRect(AREA)

    def set_dirty(self):
        self.set_modified(True)

    def set_modified(self, b):
        self.modified = b
        self.sub_window.setWindowModified(b)

    def update_title(self):
        self.sub_window.setWindowTitle(self.file_path + "[*]")

    def close_handler(self, ev):
        if not self.modified:
            return
        ret = QMessageBox().question(
            self.btree_view, "Confirm",
            "close without saving?",
            QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.No:
            ev.ignore()

    def cleanup(self):
        self.btree_scene.clear()

    def display_tree_model(self, model):
        root = self.build_tree(model.root)
        layouter = TreeNodeLayouter(root)
        layouter.run()
        self.display_links_rec(root)

    def display_links_rec(self, cur):
        spos = cur.right_pos()
        for c in cur.children:
            dpos = c.left_pos()
            l = self.btree_scene.addLine(QLineF(spos, dpos))
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
        self.btree_scene.addItem(n)
        return n

    def refresh(self):
        self.cleanup()
        self.display_tree_model(self.model)

    def selection_changed(self, graph_node, state):
        if state == 0:
            self.clean_selection_effect()
        else:
            self.current_graphics_node = graph_node
            self.show_selection_effect()

    @staticmethod
    def enlarge_rect(rect):
        offsetx = 2
        offsety = 2
        c = rect.center()
        r = QPointF(rect.width() / 2 + offsetx, rect.height() / 2 + offsety)
        return QRectF(c - r, c + r)


    def show_selection_effect(self):
        selection_pen = QPen()
        selection_pen.setWidth(5)
        rect = self.current_graphics_node.boundingRect()
        self.selection_graphics = self.btree_scene.addRect(self.enlarge_rect(rect), selection_pen)
        self.selection_graphics.setPos(self.current_graphics_node.pos())
        self.selection_graphics.setZValue(0.5)

    def clean_selection_effect(self):
        self.btree_scene.removeItem(self.selection_graphics)
        self.selection_graphics = None