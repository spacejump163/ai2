# -*- encoding: utf-8 -*-
import sys
import os

from PyQt5.QtWidgets import QTableView, QMdiSubWindow
from PyQt5.QtCore import (Qt,QAbstractTableModel, QAbstractListModel, QModelIndex, QVariant)


class InstanceVM(object):
    def __init__(self, model, parent, file_path=None):
        self.file_path = file_path
        self.model = model
        self.table_vm = InstanceTableModel(model)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_vm)
        self.table_view.show()
        self.parent = parent
        self.sub_window = parent.mdi.addSubWindow(self.table_view)
        parent.instances.append(self)

    def set_modified(self, b):
        self.sub_window.setWindowTitle("abc[*]")
        self.sub_window.setWindowModified(b)

class InstanceTableModel(QAbstractTableModel):
    def __init__(self, data_source):
        super(InstanceTableModel, self).__init__()
        self.data_source = data_source

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data_source.states)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data_source.events)

    def data(self, idx, role=Qt.DisplayRole):
        if not idx.isValid():
            return QVariant()
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        row = idx.row()
        col = idx.column()
        sid = self.data_source.states[row].uid
        eid = self.data_source.events[col].uid
        name = self.data_source.get_dst_name(sid, eid)
        return QVariant() if name is None else name

    def headerData(self, idx, orient, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return super(InstanceTableModel, self).headerData(idx, orient, role)
        if orient == Qt.Vertical:
            return self.data_source.states[idx].name + (",%s" % idx)
        else:
            return self.data_source.events[idx].name + (",%s" % idx)

    def setData(self, idx, value, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            row = idx.row()
            col = idx.column()
            sid = self.data_source.states[row].uid
            eid = self.data_source.events[col].uid
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



