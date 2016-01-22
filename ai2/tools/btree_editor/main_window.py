# -*- encoding: utf-8 -*-
import pickle
import sys
import os

from PyQt5.QtWidgets import QApplication, QFileDialog, QTabWidget, QMdiArea
from PyQt5.uic import loadUi

from ai2.tools.btree_editor.btree_config import config
from ai2.tools.btree_editor.model import \
    BTreeModel, get_all_node_class, BTreeModelPythonExporter
from tools.btree_editor.instance_vm import BTreeInstanceVM

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
        self.dock = self.window.dockWidget

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

    def close_handler(self, ev):
        l = self.mdi.subWindowList()
        if len(l) != 0:
            self.mdi.closeAllSubWindows()
            ev.ignore()

    def init_instance(self):
        self.instances = []

    def remove_instance(self, ins):
        self.instances.remove(ins)

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
        for i in self.instances:
            pth = os.path.abspath(pth)
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
                m = BTreeModel.load_file(pth)
                vm = BTreeInstanceVM(m, self, pth)

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
        fsm_files = os.listdir(config.src_path)
        for fn in fsm_files:
            full_name = os.path.join(config.src_path, fn)
            b, e = os.path.splitext(full_name)
            if e == BTREE_FILE_EXT:
                f = open(full_name, "rb")
                basename, e = os.path.splitext(fn)
                model_object = pickle.load(f)
                f.close()
                exporter = BTreeModelPythonExporter(model_object)
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
        w.instance.vm.copy_handler()

    def action_paste_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.paste_handler()

    def action_cut_handler(self):
        w = self.mdi.activeSubWindow()
        if w is None:
            return
        w.instance.vm.cut_handler()



def run():
    app = QApplication(sys.argv)
    ex = BTreeEditorMainWindow()
    app.exec_()