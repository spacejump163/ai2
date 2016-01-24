# -*- encoding: utf-8 -*-
import os
from PyQt5.QtGui import QPen

from PyQt5.QtWidgets import QGraphicsView, QMessageBox, QGraphicsScene
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF

from ai2.tools.btree_editor.tree_edit_view import \
    NodeEditorView, NodeEditorVM
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
        self.btree_view.closeEvent = self.close_handler
        parent.instances.append(self)
        self.sub_window.show()


        self.vm.refresh()

    def init_view(self):
        self.btree_scene = QGraphicsScene()
        self.btree_view = NodeEditorView(self.btree_scene)
        self.btree_view.setAttribute(Qt.WA_DeleteOnClose)
        self.btree_scene.setSceneRect(AREA)
        self.vm = NodeEditorVM(self.model, self.btree_view, self.btree_scene, self.parent)

    def set_dirty(self):
        self.set_modified(True)

    def set_modified(self, b):
        self.modified = b
        self.sub_window.setWindowModified(b)

    def update_title(self):
        self.sub_window.setWindowTitle(self.file_path + "[*]")

    def close_handler(self, ev):
        """
        if self.modified:
            ret = QMessageBox().question(
                self.btree_view, "Confirm",
                "close without saving?",
                QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                ev.ignore()
                return
        """
        self.parent.remove_instance(self)

    def activation_handler(self):
        #print("%s about to be activated" % self)
        pass

    def deactivation_handler(self):
        #print("%s about to be deactivated" % self)
        self.vm.cancel_selection()
