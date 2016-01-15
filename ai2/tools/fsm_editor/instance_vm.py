# -*- encoding: utf-8 -*-
import sys
import os

from PyQt5.QtWidgets import \
    QTableView, QMdiSubWindow, QHBoxLayout, QSizePolicy, QMessageBox
from PyQt5.QtCore import \
    Qt,QAbstractTableModel, QAbstractListModel, QModelIndex, QVariant, QSize, \
    pyqtSignal
from PyQt5.uic import loadUi


class InstanceVM(object):
    def __init__(self, model, parent, file_path):
        self.file_path = os.path.abspath(file_path)
        self.modified = False
        self.model = model
        self.table_vm = InstanceTableModel(model)
        self.table_view = QTableView()
        self.table_view.show()
        self.table_view.closeEvent = self.close_handler
        self.table_view.setModel(self.table_vm)
        self.parent = parent
        self.sub_window = parent.mdi.addSubWindow(self.table_view)
        self.sub_window.instance = self
        self.sub_window.setAttribute(Qt.WA_DeleteOnClose)
        self.table_view.setAttribute(Qt.WA_DeleteOnClose)
        self.sub_window.setWindowTitle(self.file_path + "[*]")
        self.sub_window.closeEvent = self.close_handler
        parent.instances.append(self)

    def set_dirty(self):
        self.set_modified(True)

    def set_modified(self, b):
        self.modified = b
        self.sub_window.setWindowModified(b)

    def close_handler(self, ev):
        if not self.modified:
            return
        ret = QMessageBox().question(
            self.table_view, "Confirm",
            "close without saving?",
            QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.No:
            ev.ignore()


class InstanceTableModel(QAbstractTableModel):
    def __init__(self, data_source):
        super(InstanceTableModel, self).__init__()
        self.data_source = data_source
        self.modified = pyqtSignal()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data_source.state)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data_source.event)

    def data(self, idx, role=Qt.DisplayRole):
        if not idx.isValid():
            return QVariant()
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        row = idx.row()
        col = idx.column()
        sid = self.data_source.state[row].uid
        eid = self.data_source.event[col].uid
        state = self.data_source.get_dst_state(sid, eid)
        if state:
            name = state.name
        else:
            name = None
        return QVariant() if name is None else name

    def headerData(self, idx, orient, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return super(InstanceTableModel, self).headerData(idx, orient, role)
        if orient == Qt.Vertical:
            return self.data_source.state[idx].name + (",%s" % self.data_source.state[idx].uid)
        else:
            return self.data_source.event[idx].name + (",%s" % self.data_source.event[idx].uid)

    def setData(self, idx, value, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            row = idx.row()
            col = idx.column()
            sid = self.data_source.state[row].uid
            eid = self.data_source.event[col].uid
            self.modfied.emit()
            if value == "":
                self.data_source.remove_edge(sid, eid)
                self.dataChanged.emit(self.index(row, col), self.index(row + 1, col + 1))
                return True
            else:
                did = self.data_source.get_uid_from_name(value)
                if did is None:
                    return False
                self.data_source.add_edge(sid, eid, did)
                self.dataChanged.emit(self.index(row, col), self.index(row + 1, col + 1))
                return True
        else:
            return False

    def flags(self, idx):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def refresh(self):
        self.modelReset.emit()
        self.modfied.emit()

