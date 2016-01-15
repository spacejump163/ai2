# -*- encoding: utf-8 -*-
import pickle
import pprint

import ai2.runtime.defs as defs
from ai2.tools.common_types import ParamItem

class FsmModel(object):
    def __init__(self):
        self.state = []
        self.event = []
        # note that to avoid trouble, each edge is stored as
        # (source state uid, event uid): dst state uid
        self.edge = {}
        # misc
        self.default_state_uid = None
        self.uid_cnt = 0

    def default_init(self):
        st_default = self.add_item(StateItem, "state", "default")
        st_dead = self.add_item(StateItem, "state", "dead")
        ev_born = self.add_item(EventItem, "event", "born")
        ev_die = self.add_item(EventItem, "event", "die")
        self.add_edge(st_dead.uid, ev_born.uid, st_dead.uid)

    def get_uid(self):
        self.uid_cnt += 1
        return self.uid_cnt

    def add_item(self, clz, category, name=None, ins_pos=None):
        item_list = getattr(self, category)
        if ins_pos is None:
            ins_pos = len(item_list) + 1
        if name is None:
            name = category + str(self.uid_cnt)
        for it in item_list:
            if it.name == name:
                return False
        new_item = clz(name, self.get_uid())
        item_list.insert(ins_pos, new_item)
        return new_item

    def get_item_index(self, category, uid):
        item_list = getattr(self, category)
        for i, item in enumerate(item_list):
            if item.uid == uid:
                return i
        return None

    def remove_item(self, category, item):
        if category == "event":
            self.remove_event(item)
        elif category == "state":
            self.remove_state(item)
        else:
            assert(False)

    def remove_event(self, event):
        to_del = set()
        for sid, eid in self.edge.keys():
            if eid == event.uid:
                to_del.add((sid, eid))
        for k in to_del:
            del self.edge[k]
        self.event.remove(event)

    def remove_state(self, state):
        to_del = set()
        for sid, eid in self.edge.keys():
            if sid == state.uid:
                to_del.add((sid, eid))
        for k in to_del:
            del self.edge[k]
        self.state.remove(state)

    def move_item(self, category, si, step):
        item_list = getattr(self, category)
        assert(step == 1 or step == -1)
        if si == 0 and step == -1:
            return si
        if si == len(item_list) - 1 and step == 1:
            return si
        l = si
        r = si + step
        item_list[l], item_list[r] = item_list[r], item_list[l]
        return r

    def get_item_index_from_uid(self, category, uid):
        item_list = getattr(self, category)
        for n, item in enumerate(item_list):
            if item.uid == uid:
                return n
        return None

    def get_uid_from_item_name(self, category, name):
        item_list = getattr(self, category)
        for s in item_list:
            if s.name == name:
                return s.uid
        return None

    def get_dst_state(self, sid, eid):
        k = (sid, eid)
        try:
            duid = self.edge[k]
            didx = self.get_item_index_from_uid("state", duid)
            return self.state[didx]
        except KeyError:
            return None

    def add_edge(self, sid, eid, did):
        self.edge[(sid, eid)] = did

    def remove_edge(self, sid, eid):
        try:
            del self.edge[(sid, eid)]
        except KeyError:
            pass

    def to_tuple(self):
        states = tuple([st.to_tuple() for st in self.state])
        initial_state_index = self.get_item_index_from_uid("state", self.default_state_uid)
        events = tuple([ev.name for ev in self.event])
        edges = {}
        for k, v in self.edge.items():
            sidx = self.get_item_index_from_uid("state", k[0])
            eidx = self.get_item_index_from_uid("event", k[1])
            didx = self.get_item_index_from_uid("state", v)
            edges[(sidx, eidx)] = didx
        return states, initial_state_index, events, edges

    def dump_file(self, path):
        f = open(path, "wb")
        pickle.dump(self, f)
        f.close()

    @staticmethod
    def load_file(path):
        f = open(path, "rb")
        obj = pickle.load(f)
        return obj

class StateItem(object):
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.enter_actions = []
        self.leave_actions = []

    def to_tuple(self):
        enters = tuple([act.to_tuple() for act in self.enter_actions])
        leaves = tuple([act.to_tuple() for act in self.leave_actions])
        return self.name, enters, leaves

    def add_item(self, category, ins_pos=None):
        item_list = getattr(self, category)
        if ins_pos is None:
            ins_pos = len(item_list) + 1
        new_item = ActionItem()
        item_list.insert(ins_pos, new_item)
        return new_item

    def remove_item(self, category, item):
        item_list = getattr(self, category)
        item_list.remove(item)

    def move_item(self, category, si, step):
        item_list = getattr(self, category)
        assert(step == 1 or step == -1)
        if si == 0 and step == -1:
            return si
        if si == len(item_list) - 1 and step == 1:
            return si
        l = si
        r = si + step
        item_list[l], item_list[r] = item_list[r], item_list[l]
        return r


class ActionItem(object):
    def __init__(self, method_name="action name", args=None):
        self.name = method_name
        if args is None:
            self.args = []
        else:
            self.args = args

    def to_tuple(self):
        targs = [a.to_tuple() for a in self.args]
        return tuple([self.name] + targs)

    def add_item(self, ins_pos=None):
        if ins_pos is None:
            ins_pos = len(self.args) + 1
        new_item = ParamItem(defs.PAR_CONST, "")
        self.args.insert(ins_pos, new_item)
        return new_item

    def remove_item(self, item):
        self.args.remove(item)

    def move_item(self, si, step):
        assert(step == 1 or step == -1)
        if si == 0 and step == -1:
            return si
        if si == len(self.args) - 1 and step == 1:
            return si
        l = si
        r = si + step
        self.args[l], self.args[r] = self.args[r], self.args[l]
        return r





class EventItem(object):
    def __init__(self, event_name, uid):
        self.uid = uid
        self.name = event_name


python_template = """
info = __file__

states = \\
{STATE_LIST}

initial_state_index = \\
{INITIAL_STATE_INDEX}

events = \\
{EVENT_LIST}

graph = \\
{GRAPH_DICT}

"""


class FsmModelPythonExporter(object):
    PPRINT_WIDTH = 40

    def __init__(self, fsm_model):
        self.fsm_model = fsm_model

    def export(self, file_path=None):
        states, initial, events, edges = self.fsm_model.to_tuple()
        state_list = pprint.pformat(states, width=self.PPRINT_WIDTH)
        initial_state_index = pprint.pformat(initial, width=self.PPRINT_WIDTH)
        event_list = pprint.pformat(events, width=self.PPRINT_WIDTH)
        graph_dict = pprint.pformat(edges, width=self.PPRINT_WIDTH)
        body = python_template.format(
            STATE_LIST=state_list,
            INITIAL_STATE_INDEX=initial_state_index,
            EVENT_LIST=event_list,
            GRAPH_DICT=graph_dict
        )
        if file_path:
            f = open(file_path, "wb")
            f.write(bytes(body, "utf-8"))
            f.close()
        else:
            print(body)


def test_model():
    em = FsmModel()
    hello = em.add_item(EventItem, "event", "hello world")
    em.add_item(EventItem, "event", "lost sth")
    em.add_item(EventItem, "event", "found sth")
    em.add_item(StateItem, "state", "init")
    ready = em.add_item(StateItem, "state", "ready")
    dead = em.add_item(StateItem, "state", "dead")
    act0 = ActionItem("log", [ParamItem(defs.PAR_BB, "tree.py"), ParamItem(defs.PAR_BB, "tree.py")])
    act1 = ActionItem("tree", [ParamItem(defs.PAR_BB, "tree.py"),])
    dead.enter_actions.append(act0)
    dead.enter_actions.append(act1)
    act2 = ActionItem("fsm", [ParamItem(defs.PAR_BB, "tree.py"),])
    dead.leave_actions.append(act2)
    em.add_edge(dead.uid, hello.uid, ready.uid)
    dumps = pickle.dumps(em)
    r = pickle.loads(dumps)
    exp = FsmModelPythonExporter(r)
    exp.export("d:/tmp/out.py")


def test_tuple():
    state = StateItem("", 666)
    item = state.add_item("enter_actions")
    item.add_item()
    item.add_item()
    s = str(item.to_tuple())
    print(s)
    pass


if __name__ == "__main__":
    test_tuple()
