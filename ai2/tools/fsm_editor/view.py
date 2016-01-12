# -*- encoding: utf-8 -*-
import sys
import os

from PyQt5.QtCore import (QSignalMapper, Qt)
from PyQt5.QtWidgets import (QAction, QApplication, QTableView, QTabWidget, QMdiArea)
from PyQt5.uic import loadUi

from ai2.tools.fsm_editor.instance_vm import InstanceVM
from ai2.tools.fsm_editor.model import FsmModel

MAIN_UI_PATH = os.path.join(os.path.dirname(__file__), "../../../res/gui/fsm_main.ui")

class EditorMainWindow(object):
    def __init__(self):
        self.widget = loadUi(MAIN_UI_PATH)
        self.init_mdi()
        self.init_actions()
        self.init_instance()

        self.widget.showMaximized()

    def init_mdi(self):
        self.mdi = QMdiArea(self.widget)
        self.mdi.setViewMode(QMdiArea.TabbedView)
        self.mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi.setTabsMovable(True)
        self.mdi.setTabsClosable(True)
        self.mdi.setTabShape(QTabWidget.Rounded)
        self.widget.setCentralWidget(self.mdi)

    def init_actions(self):
        self.widget.actionNew.triggered.connect(self.action_new_handler)
        self.widget.actionOpen.triggered.connect(self.action_open_handler)
        self.widget.actionSave.triggered.connect(self.action_save_handler)
        self.widget.actionSave_As.triggered.connect(self.action_save_as_handler)
        self.widget.actionClose.triggered.connect(self.action_close_handler)
        self.widget.actionClose_All.triggered.connect(self.action_close_all_handler)

    def init_instance(self):
        self.instances = []

    def action_new_handler(self):
        self.new_instance()

    def action_open_handler(self):
        pass

    def action_save_handler(self):
        pass

    def action_save_as_handler(self):
        pass

    def action_close_handler(self):
        pass

    def action_close_all_handler(self):
        pass

    def test_handler(self):
        pass

    def new_instance(self):
        m = FsmModel()
        m.default_init()
        InstanceVM(m, self)

def start_main():
    app = QApplication(sys.argv)
    ex = EditorMainWindow()
    app.exec_()
