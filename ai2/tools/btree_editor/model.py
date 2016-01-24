# -*- encoding: utf-8 -*-
import os
import pickle
import pprint

import ai2.runtime.defs as defs
from ai2.tools.btree_editor.btree_config import config
from ai2.tools.editable_objects import \
    StringValue, IntValue, FloatValue, BoolValue,\
    EnumeratorValue, \
    ListValue, StructValue, TypedValueBuilder, ChoiceProvider


class ColorProvider(ChoiceProvider):
    choices = (
        "red",
        "green",
        "yellow",
        "purple",
        "grey",
        "white",
    )
    values = choices


class NodeModel(object):
    category = "invalid_category"
    type_display_name = category

    #editable_info_template
    EIT = (
        ("comment", "\n",),
        ("color", ColorProvider),
    )

    def __init__(self):
        self.uid = 0
        self.children = []
        self.parent = None
        self.editable_info = TypedValueBuilder.build_object(self.EIT, "info")

    @property
    def debug_info(self):
        return ""

    def to_tuple(self):
        data = self.data_to_tuple()
        children = self.children_to_tuple()
        return tuple([self.category, data, children, self.debug_info])

    def data_to_tuple(self):
        return ()

    def get_name(self):
        return self.category + str(self.uid)

    def get_display_text(self):
        return self.type_display_name + str(self.uid)

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
        return tuple(self.editable_info.weights)


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

    def __init__(self):
        super(AlwaysModel, self).__init__()

    def data_to_tuple(self):
        return self.editable_info.boolean


class CallModel(NodeModel):
    category = defs.NT_CALL
    type_display_name = "Call"

    EIT = NodeModel.EIT + (("tree_name", ""),)

    def data_to_tuple(self):
        return self.editable_info.tree_name


class MethodNameProvider(object):
    choices = (
        "func0",
        "func1",
        "func2",
        "func3",
    )
    values = choices


class ParamTypeProvider(object):
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

    EIT = NodeModel.EIT + (
        ("enter", (
            ("act_name", MethodNameProvider),
        )),
        ("leave", (
            ("act_name", MethodNameProvider),
        ))
    )

    def data_to_tuple(self):
        info = self.editable_info
        return tuple([info.enter, info.leave])

    def get_display_text(self):
        itr = self.editable_info.enter.__iter__()
        func_name = itr.__next__().get_name()
        args = [repr(i) for i in itr]
        arg_str = ", ".join(map(lambda x: repr(x), args))
        return "%s(%s)" % (func_name, arg_str)


class SymbolName(object):
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return self.symbol


class CodeFragment(object):
    compile_template = """compile({CODE_BODY}, "<string>", "exec")"""

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        body = self.compile_template.format(CODE_BODY=repr(self.code))
        return body


class ConditionModel(NodeModel):
    category = defs.NT_COMP
    type_display_name = "Condition"

    arg_desc = (
        ("param_type", ParamTypeProvider),
        ("var_name", ""),
        ("expr_name", ""),
    )
    EIT = NodeModel.EIT + (
        ("expr", "\n"),
        ("iargs", [arg_desc])
    )

    def data_to_tuple(self):
        info = self.editable_info
        return info.expr, info.iargs


class ComputeModel(ConditionModel):
    category = defs.NT_COMP
    type_display_name = "Compute"

    EIT = ConditionModel.EIT + (
        ("oargs", [ConditionModel.arg_desc]),
    )

    def data_to_tuple(self):
        info = self.editable_info
        return info.expr, info.iargs, info.oargs


class WaitForModel(NodeModel):
    category = defs.NT_WAIT
    type_display_name = "WaitFor"

    EIT = NodeModel.EIT + (
        ("event", ""),
    )

    def data_to_tuple(self):
        return self.editable_info.event


class BTreeModel(object):
    def __init__(self):
        self.root = RootModel()
        self.root.uid_cnt = 0
        self.uid_cnt = 0

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
        node = clz()
        node.uid = uid
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
info = __file__

"""

file_tail = """
root = {ROOT_NAME}
"""


class BTreeModelPythonExporter(object):
    PPRINT_WIDTH = 40

    def __init__(self, btree_model):
        self.btree_model = btree_model

    def export(self, file_path=None):
        frags = [file_header]
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
