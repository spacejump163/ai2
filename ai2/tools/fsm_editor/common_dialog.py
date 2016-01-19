# -*- encoding: utf-8 -*-


from PyQt5.QtWidgets import QTreeView, QAction, QMessageBox
from PyQt5.QtCore import Qt, QAbstractItemModel, QAbstractListModel, QVariant, QModelIndex


class MultiColumnListModel(QAbstractItemModel):
    """
    this model is a view-model, it exists only to serve QTreeView
    """
    def __init__(self, data_list, attr_list, header_list):
        super(MultiColumnListModel, self).__init__()
        self.data_list = data_list
        self.attr_list = attr_list
        self.header_list = header_list

    def index(self, row, col, parent=QModelIndex(), *args, **kwargs):
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        if not parent.isValid():  # root case
            return self.createIndex(row, col, self.data_list[row])
        else:  # children get no children
            return QModelIndex()

    def parent(self, idx=QModelIndex()):
        return QModelIndex()

    def rowCount(self, idx=None, *args, **kwargs):
        if not idx.isValid():  # root
            return len(self.data_list)
        else:
            return 0  # no children for rows

    def columnCount(self, idx=QModelIndex(), *args, **kwargs):
        return len(self.header_list)

    def data(self, idx, role=None):
        if not (role == Qt.DisplayRole or role == Qt.EditRole):
            return QVariant()
        if not idx.isValid():
            return QVariant()
        data = idx.internalPointer()
        row = idx.row()
        col = idx.column()
        val = getattr(data, self.attr_list[col])
        return val

    def setData(self, idx, value, role=None):
        if role != Qt.EditRole:
            return False
        if not idx.isValid():
            return False
        data = idx.internalPointer()
        row = idx.row()
        col = idx.column()
        setattr(data, self.attr_list[col], value)
        uidx = self.createIndex(row, col)
        self.dataChanged.emit(uidx, uidx)
        return True

    def headerData(self, idx, orient, role=None):
        if role == Qt.DisplayRole and orient == Qt.Horizontal:
            return self.header_list[idx]
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
        titem = qidx.internalPointer()
        i = self.data_list.index(titem)
        return i

    def refresh(self):
        self.modelReset.emit()


class SimpleListModel(QAbstractListModel):
    def __init__(self, source_list):
        super(SimpleListModel, self).__init__()
        self.source = source_list

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.source)

    def data(self, idx, role=None):
        if idx.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
            row = idx.row()
            d = self.value_to_display(self.source[row])
            return d
        else:
            return QVariant()

    def refresh(self):
        self.modelReset.emit()

    def value_to_display(self, value):
        return str(value)

    def get_item_index(self, idx):
        row = idx.row()
        return row


class ListEditPanelVM(object):
    """
    this can be used even though the widget used to display can be
    QListView or QTreeView, button_edit may exists
    the view model for QTreeView(list_vm) is constructed outside since its ctor
    needs a lot of parameters
    """
    def __init__(self, container_vm, container_model, item_ctor, item_dtor, window):
        self.container_vm = container_vm
        self.model_list = container_model
        self.window = window
        self.ctor = item_ctor
        self.dtor = item_dtor
        self.window.view.setModel(self.container_vm)
        # setup handlers
        self.window.button_new.clicked.connect(self.new_handler)
        self.window.button_delete.clicked.connect(self.delete_handler)
        self.window.button_up.clicked.connect(self.up_handler)
        self.window.button_down.clicked.connect(self.down_handler)
        self.window.view.doubleClicked.connect(self.edit_handler)

    def change_model(self, container_vm, container_model, item_ctor, item_dtor):
        self.container_vm = container_vm
        self.model_list = container_model
        self.ctor = item_ctor
        self.dtor = item_dtor
        self.window.view.setModel(self.container_vm)

    def get_selection_index(self):
        a = self.window.view.currentIndex()
        if a.isValid():
            return self.container_vm.get_item_index(a)
        else:
            return -1

    def get_selection_position(self):
        a = self.window.view.currentIndex()
        if a.isValid():
            return a.row(), a.column()
        else:
            return None

    def set_selection(self, i):
        idx = self.container_vm.createIndex(i, 0, self.model_list[i])
        self.window.view.setCurrentIndex(idx)

    def new_handler(self):
        sel = self.get_selection_index()
        if sel < 0:
            sel = None
        else:
            sel += 1
        self.ctor(ins_pos=sel)
        self.refresh()
        self.set_selection(sel if sel is not None else 0)

    def delete_handler(self):
        i = self.get_selection_index()
        if i == -1:
            return
        self.dtor(self.model_list[i])
        self.refresh()

    def move_selection(self, si, step):
        assert(step == 1 or step == -1)
        if si == -1:
            return -1
        if si == 0 and step == -1:
            return si
        if si == len(self.model_list) - 1 and step == 1:
            return si
        l = si
        r = si + step
        self.model_list[l], self.model_list[r] = self.model_list[r], self.model_list[l]
        return r

    def up_handler(self):
        i = self.get_selection_index()
        if i == -1:
            return
        ret = self.move_selection(i, -1)
        self.refresh()
        self.set_selection(ret)

    def down_handler(self):
        i = self.get_selection_index()
        if i == -1:
            return
        ret = self.move_selection(i, 1)
        self.refresh()
        self.set_selection(ret)

    def edit_handler(self):
        """
        i = self.get_selection_index()
        self.refresh()
        self.set_selection(i)
        """
        pass

    def run(self):
        self.window.exec()

    def refresh(self):
        self.container_vm.refresh()


def test_event():
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

    headers = ("event name", "uid")
    attrs = ("name", "uid")
    list_vm = MultiColumnListModel(app_model.event, attrs, headers)
    dialog = ListEditPanelVM(
        list_vm,
        app_model.event,
        app_model.add_event,
        app_model.remove_event,
        w)
    ret = dialog.run()
    print(ret)

def test_state():
    import os
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.uic import loadUi
    from ai2.tools.fsm_editor.model import FsmModel

    app = QApplication(sys.argv)
    app_model = FsmModel()
    app_model.default_init()
    path = os.path.join(os.path.dirname(__file__), "../../../res/gui/fsm_state_list_dialog.ui")
    w = loadUi(path)

    headers = ("state name", "uid")
    attrs = ("name", "uid")
    list_vm = MultiColumnListModel(app_model.event, attrs, headers)
    dialog = ListEditPanelVM(
        list_vm,
        app_model.state,
        app_model.add_state,
        app_model.remove_event,
        w)
    ret = dialog.run()
    print(ret)