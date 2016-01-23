# -*- encoding: utf-8 -*-
import copy

from PyQt5.QtWidgets import \
    QFormLayout, QVBoxLayout,\
    QGroupBox, QComboBox, QLineEdit, QPlainTextEdit, QPushButton, \
    QHBoxLayout, QSizePolicy, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
import sys


class TypedValue(object):
    _is_container = False
    def __init__(self):
        self._name = ""
        self._v = None

    def set_name(self, name):
        self._name = name
        return self

    def get_name(self):
        return self._name

    def get_value(self):
        return self._v

    def __repr__(self):
        return repr(self._v)


class StringValue(TypedValue):
    _checker = str
    def __init__(self, v=""):
        super(StringValue, self).__init__()
        self._v = v
        if v == "\n":
            self.multi_line = True
        else:
            self.multi_line = False

    def assign(self, v):
        self._v = v

    def to_editor(self, modify_callback, current_name):
        if self.multi_line:
            return self._build_multi_line_editor(modify_callback, current_name)
        else:
            return self._build_single_line_editor(modify_callback, current_name)

    def _build_multi_line_editor(self, modify_callback, current_name):
        w = QPlainTextEdit()
        p = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        w.setSizePolicy(p)
        w.setPlainText(self._v)
        def changed():
            nv = w.toPlainText()
            self._v = nv
            modify_callback(current_name, self, w)
        w.textChanged.connect(changed)
        return w

    def _build_single_line_editor(self, modify_callback, current_name):
        w = QLineEdit()
        w.setText(str(self._v))
        def changed():  # have to use closure since we need to read from widget
            nv = w.text()
            self._v = self._checker(nv)
            modify_callback(current_name, self, w)
            w.setText(str(self._v))
        w.editingFinished.connect(changed)
        return w


class BoolValue(TypedValue):
    def __init__(self, v=True):
        super(BoolValue, self).__init__()
        self._v = v

    def assign(self, v):
        self._v = v

    def to_editor(self, modify_callback, current_name):
        w = QCheckBox()
        def changed():
            nv = w.isChecked()
            self._v = nv
            modify_callback(current_name, self, w)
        w.stateChanged.connect(changed)
        return w


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


class ChoiceProvider(object):
    values = ()
    choices = ()


class EnumeratorValue(TypedValue):
    def __init__(self, choice_provider, v=None):
        super(EnumeratorValue, self).__init__()
        if v is None:
            v = choice_provider.values[0]
        self._v = v
        self._choice_provider = choice_provider

    def assign(self, v):
        self._v = v

    def to_editor(self, modify_callback, current_name):
        w = QComboBox()
        choices = self._choice_provider.choices
        values = self._choice_provider.values
        w.addItems(choices)
        if self._v in values:
            idx = values.index(self._v)
            w.setCurrentIndex(idx)
        else:
            assert(False)  # no matching choice
        def changed(idx):
            values = self._choice_provider.values
            self._v = values[idx]
            modify_callback(current_name, self, w)

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

    def to_editor(self, modify_callback, current_name):
        box = QGroupBox()
        szp = box.sizePolicy()
        szp.setVerticalPolicy(QSizePolicy.Maximum)
        box.setSizePolicy(szp)

        layout = QVBoxLayout()
        box.setLayout(layout)

        child_editors = []
        for i, c in enumerate(self._v):
            w = c.to_editor(modify_callback, "%s[%d]" % (current_name, i))
            child_editors.append(w)
            layout.addWidget(w)
        self._build_add_del_part(child_editors, layout, box, modify_callback, current_name)
        return box

    def _build_add_del_part(self, child_editors, layout, box, modify_callback, current_name):
        def add_handler():
            new_element = self.append()
            i = len(child_editors)
            editor = new_element.to_editor(modify_callback, "%s[%d]" % (current_name, i))
            layout.insertWidget(i, editor)
            child_editors.append(editor)
            if modify_callback:
                modify_callback(current_name, self, box)
        def delete_handler():
            if len(child_editors) == 0:
                return
            self.pop()
            child_editors[-1].setParent(None)
            child_editors.pop()
            if modify_callback:
                modify_callback(current_name, self, box)

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

    def __iadd__(self, other):
        if type(other) in {tuple, list}:
            assert(not self.names_exist(*other))
            self._v += other
        else:
            assert(not self.names_exist(other))
            self._v.append(other)
        return self

    def clear_tail(self):
        self._v = self._v[:1]

    def to_editor(self, modify_callback, current_name):
        box = QGroupBox()
        szp = box.sizePolicy()
        szp.setVerticalPolicy(QSizePolicy.Maximum)
        box.setSizePolicy(szp)

        layout = QFormLayout()
        box.setLayout(layout)
        for n in self._v:
            editor_widget = n.to_editor(modify_callback, current_name + "." + n._name)
            if n._is_container:
                editor_widget.setTitle(n._name)
                layout.addRow(editor_widget)
            else:
                layout.addRow(n._name, editor_widget)
        return box

    def __getattr__(self, name):
        try: # note that even _v can be missing during deepcopy
            for i in self.__dict__["_v"]:
                if i._name == name:
                    return i
        except KeyError:
            pass
        raise AttributeError(name)

    def __iter__(self):
        return self._v.__iter__()

    def names_exist(self, *objs):
        for o in objs:
            if hasattr(self, o._name):
                return True
        return False

class TypedValueBuilder(object):
    table = {}
    @classmethod
    def build_object(cls, template, name=""):
        tp = type(template)
        m = cls.table[tp]
        o = m(template, name)
        return o

    @classmethod
    def init_map_table(cls):
        cls.table = {
            tuple: cls.build_struct,
            list: cls.build_list,
            int: cls.build_int,
            float: cls.build_float,
            bool: cls.build_bool,
            str: cls.build_str,
            type(ChoiceProvider): cls.build_enumerator,
        }

    @classmethod
    def build_struct(cls, template, name):
        s = StructValue()
        s.set_name(name)
        for name, value in template:
            v = cls.build_object(value, name)
            s += v
        return s

    @classmethod
    def build_list(cls, template, name):
        p = cls.build_object(template[0])
        if len(template) > 1:
            length = template[1]
        else:
            length = 0
        l = ListValue(p)
        l.set_name(name)
        for i in range(length):
            l.append()
        return l

    @classmethod
    def build_int(cls, template, name):
        v = IntValue(template)
        v.set_name(name)
        return v

    @classmethod
    def build_float(cls, template, name):
        v = FloatValue(template)
        v.set_name(name)
        return v

    @classmethod
    def build_bool(cls, template, name):
        v = BoolValue(template)
        v.set_name(name)
        return v

    @classmethod
    def build_str(cls, template, name):
        v = StringValue(template)
        v.set_name(name)
        return v

    @classmethod
    def build_enumerator(cls, template, name):
        v = EnumeratorValue(template)
        v.set_name(name)
        return v

    @classmethod
    def add_simple_fields(cls, struct, *field_names):
        fields = [StringValue().set_name(n) for n in field_names]
        struct += fields

TypedValueBuilder.init_map_table()


class TestChoiceProvider(ChoiceProvider):
    choices = (
        "func0",
        "func1",
        "func2"
    )
    values = choices
    params = (
        ("a", "b", "c"),
        ("aa", "bb"),
        ("type_name","a1","a2","a3"),
    )


def build_struct0():
    definition = (
        ("str0", "\n"),
        ("float0", 1.0),
        ("int0", 1),
        ("list0", [""]),
        ("struct0",
         (("a0", TestChoiceProvider),
         ),
        ),
    )
    st = TypedValueBuilder.build_object(definition, "top")
    return st


def test():
    app = QApplication(sys.argv)
    st = build_struct0()
    w = test_one_round(st)
    app.exec_()
    print(st)
    #w = test_one_round(st)
    #app.exec_()


import functools

def test_callback(data, layout, path, value, widget):
    print(">>>\npath:%s\nvalue:%s" % (path, repr(value)))
    if path == "root.struct0.a0":
        data.struct0.clear_tail()
        a0 = data.struct0.a0
        i = TestChoiceProvider.values.index(a0.get_value())
        p = TestChoiceProvider.params[i]
        TypedValueBuilder.add_simple_fields(data.struct0, *p)
        old_edit = layout.itemAt(0).widget()
        w = data.to_editor(functools.partial(test_callback, data, layout), "root")
        old_edit.setParent(None)
        layout.addWidget(w)

        print("old editor:%s" % old_edit)
        print("new editor:%s" % w)


def test_one_round(data):
    window = loadUi("../../res/gui/btree_main.ui")
    layout = window.scrollAreaWidgetContents.layout()
    layout.setAlignment(Qt.AlignTop)
    w = data.to_editor(functools.partial(test_callback, data, layout), "root")
    w.setProperty("objectName", "editor_root")
    layout.addWidget(w)
    window.show()
    return window



if __name__ == "__main__":
    test()