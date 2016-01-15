# -*- encoding: utf-8 -*-


from PyQt5.QtWidgets import QTreeView, QAction, QMessageBox
from PyQt5.QtCore import Qt, QAbstractItemModel, QVariant, QModelIndex
from PyQt5.QtGui import QKeySequence


class EventDialogTreeModel(QAbstractItemModel):
    def __init__(self, model):
        super(EventDialogTreeModel, self).__init__()
        self.data_source = model
        self.headers = ["Event名", "uid"]
        self.attr_map = ("name", "uid")

    def index(self, row, col, parent=QModelIndex(), *args, **kwargs):
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        if not parent.isValid():  # root case
            return self.createIndex(row, col, self.data_source.events[row])
        else:  # children get no children
            return QModelIndex()

    def parent(self, idx=QModelIndex()):
        return QModelIndex()

    def rowCount(self, idx=None, *args, **kwargs):
        if not idx.isValid():  # root
            return len(self.data_source.events)
        else:
            return 0  # no children for rows

    def columnCount(self, idx=QModelIndex(), *args, **kwargs):
        return len(self.headers)

    def data(self, idx, role=None):
        if not (role == Qt.DisplayRole or role == Qt.EditRole):
            return QVariant()
        if not idx.isValid():
            return QVariant()
        data = idx.internalPointer()
        row = idx.row()
        col = idx.column()
        val = getattr(data, self.attr_map[col])
        return val

    def setData(self, idx, value, role=None):
        if role != Qt.EditRole:
            return False
        if not idx.isValid():
            return False
        data = idx.internalPointer()
        row = idx.row()
        col = idx.column()
        setattr(data, self.attr_map[col], value)
        uidx = self.createIndex(row, col)
        self.dataChanged.emit(uidx, uidx)
        return True

    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return self.headers[idx]
        else:
            return QVariant()

    def flags(self, idx):
        col = idx.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if col == 0:
            return flags | Qt.ItemIsEditable
        else:
            return flags

    def get_item_index(self, qidx):  # get the index in model list from pyqt modelview index
        item = qidx.internalPointer()
        i = self.data_source.get_event_index(item.uid)
        return i

    def insert_before_index(self, i=None):
        if not self.data_source.add_event(None, i):
            assert(False)
        self.refresh()

    def remove_index(self, idx):
        ev = self.data_source.events[idx]
        self.data_source.remove_event(ev)
        self.refresh()

    def move_selection(self, idx, step=1):
        ret = self.data_source.move_event(idx, step)
        self.refresh()
        return ret

    def refresh(self):
        self.modelReset.emit()


class EventDialogVM(object):
    def __init__(self, model, window):
        self.tree_vm = EventDialogTreeModel(model)
        self.model = model
        self.view = window
        self.view.tree.setModel(self.tree_vm)
        # setup handlers
        self.view.button_new.clicked.connect(self.new_handler)
        self.view.button_delete.clicked.connect(self.delete_handler)
        self.view.button_up.clicked.connect(self.up_handler)
        self.view.button_down.clicked.connect(self.down_handler)

        act = self.debug_action = QAction("debug", self.view)
        act.setShortcut(QKeySequence("Ctrl+P"))
        act.triggered.connect(self.debug_handler)
        self.view.addAction(act)


    def debug_handler(self):
        a = self.get_selection_index()
        print(a)

    def get_selection_index(self):
        a = self.view.tree.currentIndex()
        if a.isValid():
            return self.tree_vm.get_item_index(a)
        else:
            return -1

    def set_selection(self, i):
        idx = self.tree_vm.createIndex(i, 0, self.model.events[i])
        self.view.tree.setCurrentIndex(idx)

    def new_handler(self):
        sel = self.get_selection_index()
        if sel < 0:
            sel = None
        else:
            sel += 1
        self.tree_vm.insert_before_index(sel)
        self.set_selection(sel if sel is not None else 0)

    def delete_handler(self):
        i = self.get_selection_index()
        self.tree_vm.remove_index(i)

    def up_handler(self):
        i = self.get_selection_index()
        ret = self.tree_vm.move_selection(i, -1)
        self.set_selection(ret)

    def down_handler(self):
        i = self.get_selection_index()
        ret = self.tree_vm.move_selection(i, 1)
        self.set_selection(ret)

    def run(self):
        self.view.exec()


def test():
    import os
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.uic import loadUi
    from ai2.tools.fsm_editor.model import FsmModel

    app = QApplication(sys.argv)
    app_model = FsmModel()
    app_model.default_init()
    path = os.path.join(os.path.dirname(__file__), "../../../res/gui/fsm_event_dialog.ui")
    w = loadUi(path)
    dialog = EventDialogVM(app_model, w)
    ret = dialog.run()
    print(ret)

