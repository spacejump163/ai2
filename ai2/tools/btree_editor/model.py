# -*- encoding: utf-8 -*-
import os
import pickle
import pprint

import ai2.runtime.defs as defs
from ai2.tools.btree_editor.btree_config import config
from ai2.tools.common_types import ParamItem


class NodeModel(object):
    category = None
    def __init__(self):
        self.uid = 0
        self.children = []
        self.debug_info = ""

    def to_tuple(self):
        data = self.data_to_tuple()
        children = self.children_to_tuple()
        return tuple([self.category, data, children, self.debug_info])

    def data_to_tuple(self):
        return ()

    def get_name(self):
        return self.category + str(self.uid)

    def get_display_text(self):
        return self.get_name()

    def get_name_symbol(self):
        return SymbolName(self.get_name())

    def children_to_tuple(self):
        name_list = [c.get_name_symbol() for c in self.children]
        return tuple(name_list)

    def add_child(self, node, idx):
        if idx is None:
            idx = len(self.children)
        self.children.insert(idx, node)


class RootModel(NodeModel):
    category = defs.NT_ROOT


class SequenceModel(NodeModel):
    category = defs.NT_SEQ


class RandomSequence(NodeModel):
    category = defs.NT_RSEQ


class SelectModel(NodeModel):
    category = defs.NT_SEL


class ProbabilityModel(NodeModel):
    category = defs.NT_PSEL

    def __init__(self):
        super(ProbabilityModel, self).__init__()
        self.weights = []

    def data_to_tuple(self):
        return tuple(self.weights)


class IfElseModel(NodeModel):
    category = defs.NT_IF


class ParallelModel(NodeModel):
    category = defs.NT_PARL


class UntilModel(NodeModel):
    category = defs.NT_UNTIL


class NotModel(NodeModel):
    category = defs.NT_NOT


class AlwaysModel(NodeModel):
    category = defs.NT_ALWAYS

    def __init__(self):
        super(AlwaysModel, self).__init__()
        self.value = True

    def data_to_tuple(self):
        return self.value


class CallModel(NodeModel):
    category = defs.NT_CALL

    def __init__(self):
        super(CallModel, self).__init__()
        self.tree_name = ""

    def data_to_tuple(self):
        return self.tree_name


class ActionModel(NodeModel):
    category = defs.NT_ACT

    def __init__(self):
        super(ActionModel, self).__init__()
        self.enter_action_name = ""
        self.enter_action_args = []
        self.leave_action_name = ""
        self.leave_action_args = []

    def data_to_tuple(self):
        enter_args = tuple([self.enter_action_name] + self.enter_action_args)
        leave_args = tuple([self.leave_action_name] + self.leave_action_args)
        return tuple([enter_args, leave_args])

    def get_display_text(self):
        return "%s%s" % (self.enter_action_name, repr(tuple(self.enter_action_args)))


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


class ComputeModel(NodeModel):
    category = defs.NT_COMP

    def __init__(self):
        super(ComputeModel, self).__init__()
        self.oargs = []
        self.code = ""
        self.iargs = []

    def data_to_tuple(self):
        oargs = tuple([a.to_tuple() for a in self.oargs])
        iargs = tuple([a.to_tuple() for a in self.iargs])
        return oargs, CodeFragment(self.code), iargs


class Condition(NodeModel):
    category = defs.NT_COMP

    def __init__(self):
        super(Condition, self).__init__()
        self.code = ""
        self.iargs = []

    def data_to_tuple(self):
        iargs = tuple([a.to_tuple() for a in self.iargs])
        return self.code, iargs


class WaitFor(NodeModel):
    category = defs.NT_WAIT

    def __init__(self):
        super(WaitFor, self).__init__()
        self.event_name = ""

    def data_to_tuple(self):
        return self.event_name


class BTreeModel(object):
    def __init__(self):
        self.root = RootModel()
        self.root.uid_cnt = 0
        self.uid_cnt = 0

    def get_uid(self):
        self.uid_cnt += 1
        return self.uid_cnt

    def add_node(self, parent, clz, idx):
        uid = self.get_uid()
        node = clz()
        node.uid = uid
        parent.add_child(node, idx)
        return node

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


def build_test_tree_model():
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
    a0.enter_action_name = "aaaaaaaaaaaaaaaaa0"
    seq2 = model.add_node(seq0, SequenceModel, 1)
    a1 = model.add_node(seq2, ComputeModel, 0)
    a2 = model.add_node(seq2, ComputeModel, 1)
    a3 = model.add_node(seq2, ComputeModel, 2)
    seq3 = model.add_node(seq0, SequenceModel, 3)
    a4 = model.add_node(seq3, ActionModel, 0)
    a5 = model.add_node(seq3, ActionModel, 1)
    a4.enter_action_name = "aa4"
    a5.enter_action_name = "aaa5"
    a6 = model.add_node(seq0, ActionModel, 9)
    a6.enter_action_name = "aaaaaaaaaaaaa6"
    return model


def run():
    model = build_test_tree_model()
    model.dump_file(config.src_path + "\\abc_btree.py")
    exporter = BTreeModelPythonExporter(model)
    exporter.export("btree_export.py")
