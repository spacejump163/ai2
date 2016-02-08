# -*- encoding:utf-8 -*-
import os

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QRectF, Qt

from ai2.tools.btree_editor.model import BTreeModel
from ai2.tools.btree_editor.btree_config import config
from ai2.tools.btree_editor.instance_vm import BTreeInstanceVM
from ai2.tools.btree_editor.tree_edit_view import NodeEditorView, NodeEditorVM

AREA_WIDTH = 1920 * 2.0
AREA_HEIGHT = 1080 * 2.0
AREA = QRectF(-AREA_WIDTH / 2, -AREA_HEIGHT / 2, AREA_WIDTH, AREA_HEIGHT)


class GraphInstanceVM(BTreeInstanceVM):
    @classmethod
    def get_full_path(cls, file_name):
        file_path = os.path.join(config.src_path, file_name)
        return file_path

    @classmethod
    def get_model(cls, full_path):
        if os.path.exists(full_path):
            model = BTreeModel.load_file(full_path)
            return model
        else:
            return None

    def init_view(self):
        self.btree_scene = QGraphicsScene()
        self.btree_view = NodeEditorView(self.btree_scene)
        self.btree_view.setAttribute(Qt.WA_DeleteOnClose)
        self.btree_scene.setSceneRect(AREA)
        self.vm = NodeObserverVM(self.model, self.btree_view, self.btree_scene, self)

    def close_handler(self, ev):
        self.parent.remove_instance(self)

    def set_dirty(self):
        pass


class NodeObserverVM(NodeEditorVM):
    def show_selection_effect(self):
        pass

    def clean_selection_effect(self):
        pass