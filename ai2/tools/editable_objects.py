# -*- encoding: utf-8 -*-
import copy

from PyQt5.QtWidgets import \
    QFormLayout, QVBoxLayout,\
    QGroupBox, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QMainWindow, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
import sys


class TypedValue(object):
    _is_container = False
    def __init__(self):
        self._name = ""
        self._v = None
        self._observer = None

    def set_name(self, name):
        self._name = name

    def __repr__(self):
        return repr(self._v)


class StringValue(TypedValue):
    _checker = str
    def __init__(self, v=""):
        super(StringValue, self).__init__()
        self._v = v

    def assign(self, v):
        self._v = v

    def _to_editor(self):
        w = QLineEdit()
        w.setText(str(self._v))
        def changed():  # have to use closure since we need to read from widget
            nv = w.text()
            try:
                self._v = self._checker(nv)
                if self._observer:
                    self._observer(self)
            except ValueError:
                pass
            w.setText(str(self._v))
        w.editingFinished.connect(changed)
        return w


class BoolValue(TypedValue):
    _checker = lambda x: x not in {"false", "False", 0, ""}

    def __init__(self, v=True):
        super(BoolValue, self).__init__()
        self._v = v

    def assign(self, v):
        self._v = v


class IntValue(StringValue):
    _checker = int

    def __init__(self, v=0):
        super(IntValue, self).__init__()
        self._v = v

    def assign(self, v):
        self._v = v

class FloatValue(StringValue):
    _checker = float
    def __init__(self, v=0.0):
        super(FloatValue, self).__init__()
        self._v = v

    def assign(self, v):
        self._v = v


class EnumeratorValue(TypedValue):
    def __init__(self, choice_provider, v=None):
        super(EnumeratorValue, self).__init__()
        if v is None:
            v = choice_provider.values[0]
        self._v = v
        self._choice_provider = choice_provider

    def _to_editor(self):
        w = QComboBox()
        choices = self._choice_provider.choices
        values = self._choice_provider.values
        w.addItems(choices)
        if self._v in values:
            idx = values.index(self._v)
            w.setCurrentIndex(idx)

        def changed(idx):
            values = self._choice_provider.values
            self._v = values[idx]
            if self._observer:
                self._observer(self)

        w.currentIndexChanged.connect(changed)
        return w


class ListValue(TypedValue):
    _is_container = True
    def __init__(self, prototype):
        super(ListValue, self).__init__()
        self._v = []
        self._prototype = prototype

    def append(self):
        n = copy.deepcopy(self._prototype)
        self._v.append(n)
        return n

    def pop(self):
        self._v.pop()

    def _to_editor(self):
        box = QGroupBox()
        szp = box.sizePolicy()
        szp.setVerticalPolicy(QSizePolicy.Maximum)
        box.setSizePolicy(szp)

        layout = QVBoxLayout()
        box.setLayout(layout)

        child_editors = []
        for c in self._v:
            w = c._to_editor()
            child_editors.append(w)
            layout.addWidget(w)
        self._build_add_del_part(child_editors, layout)
        return box

    def _build_add_del_part(self, child_editors, layout):
        def add_handler():
            new_element = self.append()
            editor = new_element._to_editor()
            layout.insertWidget(len(child_editors), editor)
            child_editors.append(editor)
            if self._observer:
                self._observer(self)
        def delete_handler():
            if len(child_editors) == 0:
                return
            self.pop()
            child_editors[-1].setParent(None)
            child_editors.pop()
            if self._observer:
                self._observer(self)

        button_add = QPushButton("+")
        button_add.clicked.connect(add_handler)
        button_delete = QPushButton("-")
        button_delete.clicked.connect(delete_handler)
        hlayout = QHBoxLayout()
        hlayout.addWidget(button_add)
        hlayout.addWidget(button_delete)
        layout.addLayout(hlayout)

    def __getitem__(self, key):
        return self._v[key]

    def __iter__(self, *args, **kwargs):
        return self._v.__iter__(*args, **kwargs)


class StructValue(TypedValue):
    _is_container = True
    def __init__(self, *args):
        super(StructValue, self).__init__()
        self._v = list(args)

    def _add(self, *args):
        self._v.append += args

    def _clear_tail(self):
        self._v = self._v[:1]

    def _to_editor(self):
        box = QGroupBox()
        szp = box.sizePolicy()
        szp.setVerticalPolicy(QSizePolicy.Maximum)
        box.setSizePolicy(szp)

        layout = QFormLayout()
        box.setLayout(layout)
        for n in self._v:
            editor_widget = n._to_editor()
            if n._is_container:
                editor_widget.setTitle(n._name)
                layout.addRow(editor_widget)
            else:
                layout.addRow(n._name, editor_widget)
        return box

    def __getattr__(self, name):
        for i in self._v:
            if i._name == name:
                return i
        raise AttributeError("no %s in %s" % (name, self))


def build_struct0():
    i = IntValue()
    i.set_name("i0")
    s = StringValue()
    s.set_name("s0")
    f = FloatValue()
    f.set_name("f0")
    l = ListValue(IntValue())
    l.set_name("l0")
    l.append()
    l.append()
    l[1].assign(2)
    l[0].assign(4)
    st = StructValue(i, s, f, l)
    st.set_name("top")
    i = st.i0
    s = st.s0
    f = st.f0
    l = st.l0
    return st


def test():
    app = QApplication(sys.argv)
    window = loadUi("../../res/gui/btree_main.ui")
    layout = window.scrollAreaWidgetContents.layout()
    layout.setAlignment(Qt.AlignTop)
    st = build_struct0()
    w = st._to_editor()
    layout.addWidget(w)
    window.show()
    app.exec_()



if __name__ == "__main__":
    test()