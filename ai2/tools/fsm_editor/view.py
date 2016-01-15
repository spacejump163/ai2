# -*- encoding: utf-8 -*-
import sys
import os

import functools

from PyQt5.QtCore import QSignalMapper, Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QAction, QApplication, QTableView, QTabWidget, QMdiArea
from PyQt5.uic import loadUi

from ai2.tools.fsm_editor.instance_vm import InstanceVM
from ai2.tools.fsm_editor.model import FsmModel, EventItem, StateItem
from ai2.tools.fsm_editor.common_dialog import \
    SimpleListModel, MultiColumnListModel, ListEditPanelVM
from ai2.tools.fsm_editor.state_dialog import StateListPanelVM

this_path = os.path.dirname(__file__)
MAIN_UI_PATH = os.path.join(this_path, "../../../res/gui/fsm_main.ui")
EVENT_DIALOG_PATH = os.path.join(this_path, "../../../res/gui/fsm_event_dialog.ui")
STATE_LIST_DIALOG_PATH = os.path.join(this_path, "../../../res/gui/fsm_state_list_dialog.ui")


EVENT_DIALOG_HEADERS = ("event name", "uid")
STATE_DIALOG_HEADERS = ("state name", "uid")
LIST_DIALOG_COLUMNS = ("name", "uid")
FSM_FILE_EXT = ".fsm"

class EditorMainWindow(object):
    def __init__(self):
        self.seq = 0
        self.widget = loadUi(MAIN_UI_PATH)
        self.init_mdi()
        self.init_actions()
        self.init_instance()
        self.widget.closeEvent = self.close_handler

        self.widget.showMaximized()

    def get_seq(self):
        self.seq += 1
        return self.seq

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

        self.widget.actionStates.triggered.connect(self.action_states_handler)
        self.widget.actionEvents.triggered.connect(self.action_events_handler)

    def close_handler(self, ev):
        l = self.mdi.subWindowList()
        if len(l) != 0:
            self.mdi.closeAllSubWindows()
            ev.ignore()

    def init_instance(self):
        self.instances = []

    def action_new_handler(self):
        tmp_path = "NewFsm" + str(self.get_seq()) + FSM_FILE_EXT
        m = FsmModel()
        m.default_init()
        vm = InstanceVM(m, self, tmp_path)
        vm.set_modified(True)

    def action_open_handler(self):
        p = QFileDialog()
        p.setViewMode(QFileDialog.List)
        p.setFileMode(QFileDialog.ExistingFiles)
        p.exec()
        paths = p.selectedFiles()
        for pth in paths:
            m = FsmModel.load_file(pth)
            vm = InstanceVM(m, self, pth)

    def action_save_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        model = w.instance.model
        model.dump_file(w.instance.file_path)
        w.instance.set_modified(False)

    def action_save_as_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return

        p = QFileDialog()
        p.setViewMode(QFileDialog.List)
        p.exec()
        paths = p.selectedFiles()
        if len(paths) == 0:
            return
        w.instance.file_path = os.path.abspath(paths[0])
        model = w.instance.model
        model.dump_file(w.instance.file_path)
        w.instance.set_modified(False)

    def action_close_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.close_handler()

    def action_close_all_handler(self):
        self.mdi.closeAllSubWindows()

    def action_states_handler(self):
        cur = self.get_current_instance()
        if cur is None:
            return
        model = cur.model
        w = loadUi(STATE_LIST_DIALOG_PATH)
        list_vm = MultiColumnListModel(
            model.state,
            LIST_DIALOG_COLUMNS,
            STATE_DIALOG_HEADERS)
        add_item = functools.partial(model.add_item, StateItem, "state")
        remove_item = functools.partial(model.remove_item, "state")
        dialog = StateListPanelVM(
            list_vm,
            model.state,
            add_item,
            remove_item,
            w)

        dialog.run()
        cur.table_vm.refresh()

    def action_events_handler(self):
        cur = self.get_current_instance()
        if cur is None:
            return
        model = cur.model
        w = loadUi(EVENT_DIALOG_PATH)
        list_vm = MultiColumnListModel(
            model.event,
            LIST_DIALOG_COLUMNS,
            EVENT_DIALOG_HEADERS)
        add_item = functools.partial(model.add_item, EventItem, "event")
        remove_item = functools.partial(model.remove_item, "event")
        dialog = ListEditPanelVM(
            list_vm,
            model.event,
            add_item,
            remove_item,
            w)
        dialog.run()
        cur.table_vm.refresh()

    def get_current_instance(self):
        current = self.mdi.activeSubWindow()
        if not current:
            return None
        for i in self.instances:
            if i.sub_window == current:
                return i
        assert(False)  # there is an active sub window but there's no matching instance


def start_main():
    app = QApplication(sys.argv)
    ex = EditorMainWindow()
    app.exec_()
