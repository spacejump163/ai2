# -*- encoding: utf-8 -*-
import json
import pickle
import sys
import os

from PyQt5.QtWidgets import QApplication, QFileDialog, QTabWidget, QMdiArea, QDialog
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

from ai2.tools.btree_editor.btree_config import config
from ai2.tools.btree_editor.model import \
    BTreeModel, get_all_node_class, BTreeModelPythonExporter
from ai2.tools.btree_editor.instance_vm import BTreeInstanceVM

this_path = os.path.dirname(__file__)
MAIN_UI_PATH = os.path.join(
    this_path,
    "../../../res/gui/btree_main.ui")


BTREE_FILE_EXT = ".btree"


class BTreeEditorMainWindow(object):
    def __init__(self):
        self.init_instance()
        self.init_widgets()
        self.init_actions()
        self.init_common_logic()
        self.window.closeEvent = self.close_handler
        self.window.showMaximized()

    def init_widgets(self):
        self.seq = 0
        self.window = loadUi(MAIN_UI_PATH)
        self.mdi = self.window.mdiArea
        self.mdi.setViewMode(QMdiArea.TabbedView)
        self.mdi.setTabsMovable(True)
        self.mdi.setTabsClosable(True)
        self.mdi.setTabShape(QTabWidget.Rounded)
        self.mdi.subWindowActivated.connect(self.active_subwindow_changed)
        self.dock_content_cnt = 0
        self.dock_anchor = self.window.dockAnchor
        self.dock_anchor.layout().setAlignment(Qt.AlignTop)

    def init_actions(self):
        self.window.actionNew.triggered.connect(self.action_new_handler)
        self.window.actionOpen.triggered.connect(self.action_open_handler)
        self.window.actionSave.triggered.connect(self.action_save_handler)
        self.window.actionSave_As.triggered.connect(self.action_save_as_handler)

        self.window.actionClose.triggered.connect(self.action_close_handler)
        self.window.actionClose_All.triggered.connect(self.action_close_all_handler)
        self.window.actionExport.triggered.connect(self.action_export_handler)

        self.window.actionInsert.triggered.connect(self.action_insert_handler)
        self.window.actionDelete.triggered.connect(self.action_delete_handler)
        self.window.actionCopy.triggered.connect(self.action_copy_handler)
        self.window.actionPaste.triggered.connect(self.action_paste_handler)
        self.window.actionCut.triggered.connect(self.action_cut_handler)
        self.window.actionMoveUp.triggered.connect(self.action_move_up_handler)
        self.window.actionMoveDown.triggered.connect(self.action_move_down_handler)

        self.window.actionAgent.triggered.connect(self.action_select_agent_handler)

    def init_common_logic(self):
        self.tree_fragment = None

        self.active_instance = None

    def close_handler(self, ev):
        l = self.mdi.subWindowList()
        if len(l) != 0:
            self.mdi.closeAllSubWindows()
            ev.ignore()

    def init_instance(self):
        self.instances = []

    def remove_instance(self, ins):
        self.instances.remove(ins)

    def add_instance(self, ins):
        self.instances.append(ins)

    def add_dock_content(self, widget):
        self.clear_dock_contents()
        self.dock_anchor.layout().addWidget(widget)

    def get_dock_contents(self):
        l = self.dock_anchor.layout()
        ret = []
        for i in range(l.count()):
            ret.append(l.itemAt(i).widget())
        return ret

    def clear_dock_contents(self):
        ws = self.get_dock_contents()
        for w in ws:
            w.deleteLater()

    def get_seq(self):
        self.seq += 1
        return self.seq

    def find_non_existing_name(self):
        while True:
            tmp_path = os.path.join(
                config.src_path,
                "NewBTree" + str(self.get_seq()) + BTREE_FILE_EXT)
            if not os.path.exists(tmp_path):
                return tmp_path

    def action_new_handler(self):
        tmp_path = self.find_non_existing_name()
        m = BTreeModel()
        vm = BTreeInstanceVM(m, self, tmp_path)
        vm.set_modified(True)

    def file_already_open(self, pth):
        pth = os.path.abspath(pth)
        for i in self.instances:
            if pth == i.file_path:
                return i
        return None

    def action_open_handler(self):
        p = QFileDialog()
        p.setViewMode(QFileDialog.List)
        p.setFileMode(QFileDialog.ExistingFiles)
        p.setDirectory(config.src_path)
        p.exec()
        paths = p.selectedFiles()
        for pth in paths:
            i = self.file_already_open(pth)
            if i:
                self.mdi.setActiveSubWindow(i.sub_window)
            else:
                try:
                    m = BTreeModel.load_file(pth)
                    vm = BTreeInstanceVM(m, self, pth)
                except PermissionError:
                    pass

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
        p.setDirectory(config.src_path)
        p.exec()
        paths = p.selectedFiles()
        if len(paths) == 0:
            return
        w.instance.file_path = os.path.abspath(paths[0])
        w.instance.update_title()
        model = w.instance.model
        model.dump_file(w.instance.file_path)
        w.instance.set_modified(False)

    def action_close_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.close()

    def action_close_all_handler(self):
        self.mdi.closeAllSubWindows()

    def action_export_handler(self):
        files = os.listdir(config.src_path)
        for fn in files:
            full_name = os.path.join(config.src_path, fn)
            b, e = os.path.splitext(full_name)
            if e == BTREE_FILE_EXT:
                f = open(full_name, "rb")
                basename, e = os.path.splitext(fn)
                model_object = pickle.load(f)
                f.close()
                exporter = BTreeModelPythonExporter(model_object, src_hint=fn)
                exporter.export(os.path.join(config.export_path, basename + "_btree.py"))

    def action_insert_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.insert_handler()

    def action_delete_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.delete_handler()

    def action_copy_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        self.tree_fragment =  w.instance.vm.copy_handler()

    def action_paste_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.paste_handler(self.tree_fragment)

    def action_cut_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        self.tree_fragment = w.instance.vm.cut_handler()

    def action_move_up_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.switch_node_handler(-1)

    def action_move_down_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.switch_node_handler(1)

    def action_select_agent_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        ret = SelectAgentDialog(w.instance.model.agent_class_name).run()
        if ret is not None:
            w.instance.model.agent_class_name = ret

    def active_subwindow_changed(self, subwindow):
        if subwindow and self.active_instance and subwindow is self.active_instance.sub_window:
            return
        prev_instance = self.active_instance
        next_instance = None
        if subwindow is not None:
            for i in self.instances:
                if i.sub_window is subwindow:
                    next_instance = i
                    break
            else:
                assert(False) # can't find an existing subwindow?!
        if prev_instance:
            prev_instance.deactivation_handler()
        if next_instance:
            next_instance.activation_handler()
        self.active_instance = next_instance


SELECT_AGENT_UI_PATH = os.path.join(
    this_path,
    "../../../res/gui/btree_select_agent_dialog.ui")


class SelectAgentDialog(object):
    def __init__(self, current):
        self.window = loadUi(SELECT_AGENT_UI_PATH)
        self.list = self.window.listWidget
        with open(config.action_info_path) as action_info_file:
            info = json.load(action_info_file)
        self.keys = keys = list(info.keys())
        for i in keys:
            self.list.addItem(i)
        if current in info:
            self.list.setCurrentRow(keys.index(current))
        else:
            self.list.setCurrentRow(0)


    def run(self):
        ret = self.window.exec()
        if ret == QDialog.Accepted:
            row = self.list.currentRow()
            return self.keys[row]
        else:
            return None

def run():
    app = QApplication(sys.argv)
    ex = BTreeEditorMainWindow()
    app.exec_()