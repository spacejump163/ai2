# -*- encoding: utf-8 -*-
import json
import os
import pickle
import pprint
import logging

import ai2.runtime.defs as defs
from ai2.tools.btree_editor.btree_config import config
from ai2.tools.editable_objects import \
    StringValue, IntValue, FloatValue, BoolValue,\
    EnumeratorValue, \
    ListValue, StructValue, TypedValueBuilder, ChoiceProvider


logger = logging.getLogger("ai2.tools.btree_editor")


class ColorProvider(ChoiceProvider):
    from PyQt5.QtCore import Qt
    choices = (
        "green",
        "red",
        "yellow",
        "gray",
        "white",
        "blue",
        "cyan",
    )
    values = (
        Qt.green,
        Qt.red,
        Qt.yellow,
        Qt.gray,
        Qt.white,
        Qt.blue,
        Qt.cyan,
    )
    del Qt


class NodeModel(object):
    category = "invalid_category"
    type_display_name = category

    # editable_info_template
    EIT = (
        ("name", ""),
        ("comment", "\n",),
        ("color", ColorProvider),
    )

    def __init__(self, uid, tree):
        self.tree = tree
        self.uid = uid
        self.children = []
        self.parent = None
        self.editable_info = TypedValueBuilder.build_object(self.EIT, "info")

    @property
    def debug_info(self):
        return SymbolName("__src_file__"), self.uid

    def to_tuple(self):
        data = self.data_to_tuple()
        children = self.children_to_tuple()
        return tuple([self.category, data, children, self.debug_info])

    def data_to_tuple(self):
        return ()

    def get_name(self):
        return self.category + str(self.uid)

    def get_bg_color(self):
        return self.editable_info.color.get_value()

    def get_display_text(self):
        s = self.editable_info.name.get_value()
        if s == "":
            return self.type_display_name + str(self.uid)
        else:
            return s

    def get_name_symbol(self):
        return SymbolName(self.get_name())

    def children_to_tuple(self):
        name_list = [c.get_name_symbol() for c in self.children]
        return tuple(name_list)

    def add_child(self, node, idx):
        if idx is None:
            idx = len(self.children)
        self.children.insert(idx, node)
        node.parent = self

    def get_editor(self, refresh_handler):

        def callback(path, node, editor):
            refresh_handler()

        return self.editable_info.to_editor(
            callback,
            self.editable_info.get_name())


class RootModel(NodeModel):
    category = defs.NT_ROOT
    type_display_name = "Root"


class SequenceModel(NodeModel):
    category = defs.NT_SEQ
    type_display_name = "Sequence"

class RandomSequenceModel(NodeModel):
    category = defs.NT_RSEQ
    type_display_name = "RandomSequence"


class SelectModel(NodeModel):
    category = defs.NT_SEL
    type_display_name = "Select"


class ProbabilityModel(NodeModel):
    category = defs.NT_PSEL
    type_display_name = "Probability"

    EIT = NodeModel.EIT + (("weight", [1.0]),)

    def data_to_tuple(self):
        weights = [w.get_value() for w in self.editable_info.weight]
        if len(weights) != len(self.children):
            logger.fatal("probability weight length doesn't match children length")
            if len(weights) > len(self.children):
                weights = weights[:len(self.children)]
            else:
                if len(weights) == 0:
                    weights = [1] * len(self.children)
                else:
                    weights += [weights[-1]] * (len(weights) - len(self.children))
        distribution = list(weights)
        length = len(distribution)
        if length == 1:
            return (1,)

        for i in range(1,length):
            distribution[i] += distribution[i-1]

        return tuple(distribution)


class IfElseModel(NodeModel):
    category = defs.NT_IF
    type_display_name = "IfElse"


class ParallelModel(NodeModel):
    category = defs.NT_PARL
    type_display_name = "Parallel"


class UntilModel(NodeModel):
    category = defs.NT_UNTIL
    type_display_name = "Until"


class NotModel(NodeModel):
    category = defs.NT_NOT
    type_display_name = "Not"


class AlwaysModel(NodeModel):
    category = defs.NT_ALWAYS
    type_display_name = "Always"

    EIT = NodeModel.EIT + (("truth_value", True),)

    def data_to_tuple(self):
        return self.editable_info.truth_value.get_value()


class CallModel(NodeModel):
    category = defs.NT_CALL
    type_display_name = "Call"

    EIT = NodeModel.EIT + (("tree_name", ""),)

    def data_to_tuple(self):
        return self.editable_info.tree_name


def init_action_data(class_name):
    choices = ["no action"]
    values = [""]
    arglists = [()]
    with open(config.action_info_path) as action_info_file:
        info = json.load(action_info_file)
    class_info = info[class_name]
    choices += [i[0] for i in class_info]
    values += [i[0] for i in class_info]
    arglists += [i[1:] for i in class_info]
    return choices, values, arglists


class MethodNameProvider(ChoiceProvider):
    with open(config.action_info_path) as action_info_file:
        info = json.load(action_info_file)

    @property
    def choices(self):
        default = ["no action"]
        class_info = self.info[self.class_name]
        return default + [i[0] for i in class_info]

    @property
    def values(self):
        default = [""]
        class_info = self.info[self.class_name]
        return default + [i[0] for i in class_info]

    @property
    def arglists(self):
        default = [()]
        class_info = self.info[self.class_name]
        return default + [i[1:] for i in class_info]

    def __init__(self, class_name):
        self.class_name = class_name


class ParamTypeProvider(ChoiceProvider):
    values = (
        defs.PAR_CONST,
        defs.PAR_BB,
        defs.PAR_PROP,
    )
    choices = (
        "常数",
        "黑板值",
        "对象属性",
    )


class ActionModel(NodeModel):
    category = defs.NT_ACT
    type_display_name = "Action"

    arg_desc = (
        ("param_type", ParamTypeProvider),
        ("var_name", ""),
    )

    @property
    def EIT(self):
        template = NodeModel.EIT + (
            ("enter", (
                ("act_name", MethodNameProvider(self.tree.agent_class_name)),
            )),
            ("leave", (
                ("act_name", MethodNameProvider(self.tree.agent_class_name)),
            ))
        )
        return template

    @staticmethod
    def translate_action_struct(astruct):
        itr = astruct.__iter__()
        l = [itr.__next__().get_value()]
        while True:
            try:
                a = itr.__next__()
                tp = a.param_type.get_value()
                if tp == defs.PAR_CONST:
                    l.append((defs.PAR_CONST, eval(a.var_name.get_value())))
                else:
                    l.append((tp, a.var_name.get_value()))
            except StopIteration:
                break
        return l

    def data_to_tuple(self):
        info = self.editable_info
        return self.translate_action_struct(info.enter),\
               self.translate_action_struct(info.leave)

    @staticmethod
    def format_param(param):
        tp = param.param_type.get_value()
        if tp == defs.PAR_CONST:
            return "C(%s)" % param.var_name.get_value()
        elif tp == defs.PAR_BB:
            return "B(%s)" % param.var_name.get_value()
        elif tp == defs.PAR_PROP:
            return "P(%s)" % param.var_name.get_value()
        else:
            assert(False)

    def get_display_text(self):
        s = self.editable_info.name.get_value()
        if s != "":
            return s
        itr = self.editable_info.enter.__iter__()
        func_name = itr.__next__().get_value()
        if func_name != "":
            arg_str = ", ".join(map(self.format_param, itr))
            return "%s(%s)" % (func_name, arg_str)
        else:
            return super().get_display_text()

    def get_editor(self, refresh_handler):

        def callback(path, node, editor):
            if path == "info.enter.act_name":
                parent = self.editable_info.enter
                idx = parent.act_name.get_index()
                arglist = node._choice_provider.arglists[idx]
                parent.clear_tail()
                TypedValueBuilder.add_fields_with_template(parent, self.arg_desc, *arglist)
            elif path == "info.leave.act_name":
                parent = self.editable_info.leave
                idx = parent.act_name.get_index()
                arglist = node._choice_provider.arglists[idx]
                parent.clear_tail()
                TypedValueBuilder.add_fields_with_template(parent, self.arg_desc, *arglist)
            refresh_handler()

        w = self.editable_info.to_editor(
            callback,
            self.editable_info.get_name())
        return w

class SymbolName(object):
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return self.symbol


class CodeFragment(object):
    compile_template = """compile({CODE_BODY}, "<string>", {MODE})"""
    def __init__(self, code, flag="exec"):
        self.code = code
        self.flag = flag

    def __repr__(self):
        body = self.compile_template.format(
            CODE_BODY=repr(self.code),
            MODE=repr(self.flag)
        )
        return body


def translate_args(args):
    l = []
    for a in args:
        if a.param_type.get_value() == defs.PAR_CONST:
            l.append(
                (defs.PAR_CONST,
                 eval(a.var_name.get_value()),
                 a.expr_name.get_value()))
        else:
            l.append(a)
    return l


class ConditionModel(NodeModel):
    category = defs.NT_COND
    type_display_name = "Condition"

    arg_desc = (
        ("param_type", ParamTypeProvider),
        ("var_name", ""),
        ("expr_name", ""),
    )

    EIT = NodeModel.EIT + (
        ("expr", ""),
        ("iargs", [arg_desc]),
    )

    def get_display_text(self):
        s = self.editable_info.name.get_value()
        if s != "":
            return s
        return self.editable_info.expr.get_value()

    def data_to_tuple(self):
        info = self.editable_info
        return CodeFragment(info.expr, "eval"), translate_args(info.iargs)


class ComputeModel(NodeModel):
    category = defs.NT_COMP
    type_display_name = "Compute"

    arg_desc = (
        ("param_type", ParamTypeProvider),
        ("var_name", ""),
        ("expr_name", ""),
    )

    EIT = NodeModel.EIT + (
        ("expr", "\n"),
        ("iargs", [arg_desc]),
        ("oargs", [arg_desc]),
    )

    def data_to_tuple(self):
        info = self.editable_info
        return CodeFragment(info.expr, "exec"), \
               translate_args(info.iargs), \
               translate_args(info.oargs)


class WaitForModel(NodeModel):
    category = defs.NT_WAIT
    type_display_name = "WaitFor"

    EIT = NodeModel.EIT + (
        ("event", ""),
    )

    def get_display_text(self):
        return "Wait(%s)" % self.editable_info.event.get_value()

    def data_to_tuple(self):
        return self.editable_info.event


class BTreeModel(object):
    def __init__(self):
        self.root = RootModel(0, self)
        self.uid_cnt = 0
        self.agent_class_name = "ActionAgent"

    def get_uid(self):
        self.uid_cnt += 1
        return self.uid_cnt

    def add_node(self, parent, stuff, idx):
        if isinstance(stuff, NodeModel):
            return self.add_node_subtree(parent, stuff, idx)
        else:
            return self.add_node_clz(parent, stuff, idx)

    def add_node_clz(self, parent, clz, idx):
        uid = self.get_uid()
        node = clz(uid, self)
        parent.add_child(node, idx)
        return node

    def add_node_subtree(self, parent, subtree, idx):
        self.reuid_walker(subtree)
        parent.add_child(subtree, idx)

    def reuid_walker(self, root):
        root.uid = self.get_uid()
        for c in root.children:
            self.reuid_walker(c)

    def cut_tree(self, node):
        parent = node.parent
        parent.children.remove(node)
        node.parent = None

    def switch_sibling(self, node, step):
        c = node.parent.children
        if node.parent is None:
            return
        i = c.index(node)
        ni = i + step
        if ni < 0 or ni >= len(node.parent.children):
            return
        c[ni], c[i] = c[i], c[ni]

    def get_node(self, uid):
        return self.get_node_recursive(self.root, uid)

    def get_node_recursive(self, node, uid):
        if node.uid == uid:
            return node
        for c in node.children:
            r = self.get_node_recursive(c, uid)
            if r is not None:
                return r
        return None

    def dump_file(self, path):
        pdir = os.path.dirname(path)
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        with open(path, "wb") as ofile:
            pickle.dump(self, ofile)

    @staticmethod
    def load_file(path):
        f = open(path, "rb")
        obj = pickle.load(f)
        return obj


node_template = """
{NODE_NAME} = {NODE_BODY}

"""

file_header = """
# -*- encoding: utf-8 -*-
__src_file__ = {SRC_FILE}
"""

file_tail = """
root = {ROOT_NAME}
"""


class BTreeModelPythonExporter(object):
    PPRINT_WIDTH = 40

    def __init__(self, btree_model, src_hint=""):
        self.btree_model = btree_model
        self.src_hint = src_hint

    def export(self, file_path=None):
        frags = [file_header.format(SRC_FILE=repr(self.src_hint))]
        self.dump_recursive(self.btree_model.root, frags)
        tail_def = file_tail.format(ROOT_NAME=self.btree_model.root.get_name())
        frags.append(tail_def)
        body = "".join(frags)
        if file_path:
            pdir = os.path.dirname(file_path)
            if pdir != "" and not os.path.exists(pdir):
                os.makedirs(pdir)
            with open(file_path, "w", encoding="utf-8") as ofile:
                ofile.write(body)
        else:
            print(body)

    def dump_recursive(self, node, frags):
        for c in node.children:
            self.dump_recursive(c, frags)
        self.dump_node(node, frags)

    def dump_node(self, node, frags):
        pbody = pprint.pformat(node.to_tuple(), width=self.PPRINT_WIDTH)
        frag = node_template.format(
            NODE_NAME=node.get_name(),
            NODE_BODY=pbody)
        frags.append(frag)


def build_test_tree_model0():
    """
    root---seq0---seq1---a0
               |--seq2---a1
               |      |--a2
               |      |--a3
               |--seq3---a4
               |      |--a5
               |--a6
    """
    model = BTreeModel()
    seq0 = model.add_node(model.root, SequenceModel, 0)
    seq1 = model.add_node(seq0, SequenceModel, 0)
    a0 = model.add_node(seq1, ActionModel, 0)
    seq2 = model.add_node(seq0, SequenceModel, 1)
    a1 = model.add_node(seq2, ComputeModel, 0)
    a2 = model.add_node(seq2, ComputeModel, 1)
    a3 = model.add_node(seq2, ComputeModel, 2)
    seq3 = model.add_node(seq0, SequenceModel, 3)
    a4 = model.add_node(seq3, ActionModel, 0)
    a5 = model.add_node(seq3, ActionModel, 1)
    a6 = model.add_node(seq0, ActionModel, 9)
    return model

def build_test_tree_model1():
    model = BTreeModel()
    seq0 = model.add_node(model.root, SequenceModel, 0)
    seq1 = model.add_node(seq0, SequenceModel, 0)
    a0 = model.add_node(seq1, ActionModel, 0)
    return model

def get_all_node_class():
    classes = [
        SequenceModel,
        RandomSequenceModel,
        SelectModel,
        ProbabilityModel,
        IfElseModel,
        ParallelModel,
        UntilModel,
        NotModel,
        AlwaysModel,
        CallModel,
        ActionModel,
        ComputeModel,
        ConditionModel,
        WaitForModel,
    ]
    return classes


def run():
    model = build_test_tree_model1()
    model.dump_file(config.src_path + "\\abc_btree.btree")
    exporter = BTreeModelPythonExporter(model)
    exporter.export()
