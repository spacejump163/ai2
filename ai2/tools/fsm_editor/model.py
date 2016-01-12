# -*- encoding: utf-8 -*-
import pickle
import pprint

import ai2.runtime.defs as defs


class FsmModel(object):
    def __init__(self):
        self.states = []
        self.events = []
        self.edges = {}
        # misc
        self.default_state_uid = None
        self.uid_cnt = 0

    def default_init(self):
        self.add_state("default")
        self.add_state("dead")
        self.add_event("born")
        self.add_event("die")

    def get_uid(self):
        self.uid_cnt += 1
        return self.uid_cnt

    def dump(self):
        pass

    def load(self, data):
        pass

    def add_event(self, event_name):
        for ev in self.events:
            if ev.name == event_name:
                return False
        nev = EventItem(event_name, self.get_uid())
        self.events.append(nev)
        return nev

    def get_event_index(self, uid):
        for i, ev in enumerate(self.events):
            if ev.uid == uid:
                return i

    def remove_event(self, event):
        to_del = set()
        for sid, eid in self.edges.keys():
            if eid == event.uid:
                to_del.add((sid, eid))
        for k in to_del:
            del self.edges[k]
        self.events.remove(event)

    def add_state(self, state_name):
        for st in self.states:
            if st.name == state_name:
                return False
        nst = StateItem(state_name, self.get_uid())
        self.states.append(nst)
        return nst

    def get_state_index_from_uid(self, uid):
        for i, st in enumerate(self.states):
            if st.uid == uid:
                return i
        return None

    def get_uid_from_name(self, name):
        for s in self.states:
            if s.name == name:
                return s.uid
        return None

    def get_state_name(self, uid):
        for i, s in enumerate(self.states):
            if s.uid == uid:
                return s.name
        return "?!: got no corresponding name for dst uid"

    def get_dst_name(self, sid, eid):
        k = (sid, eid)
        try:
            did = self.edges[k]
            return self.get_state_name(did)
        except KeyError:
            return None

    def remove_state(self, state):
        to_del = set()
        for sid, eid in self.edges.keys():
            if sid == state.uid:
                to_del.add((sid, eid))
        for k in to_del:
            del self.edges[k]
        self.states.remove(state)

    def add_edge(self, sid, eid, did):
        self.edges[(sid, eid)] = did

    def remove_edge(self, sid, eid):
        try:
            del self.edges[(sid, eid)]
        except KeyError:
            pass

    def to_tuple(self):
        states = tuple([st.to_tuple() for st in self.states])
        initial_state_index = self.default_state_uid
        events = tuple([ev.name for ev in self.events])
        edges = {}
        for k, v in self.edges.items():
            sidx = self.get_state_index_from_uid(k[0])
            eidx = self.get_state_index_from_uid(k[1])
            vidx = self.get_state_index_from_uid(v)
            edges[(sidx, eidx)] = vidx
        return states, initial_state_index, events, edges


class StateItem(object):
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.enter_actions = []
        self.leave_actions = []

    def to_tuple(self):
        enters = tuple([act.to_tuple() for act in self.enter_actions])
        leaves = tuple([act.to_tuple() for act in self.leave_actions])
        return enters, leaves, self.name


class ActionItemCall(object):
    def __init__(self, method_name, args):
        self.name = method_name
        self.args = args

    def to_tuple(self):
        return tuple([defs.SA_CALL, self.name] + self.args)


class ActionItemState(object):
    def __init__(self, state_name):
        self.name = state_name

    def to_tuple(self):
        return defs.SA_GRAPH, self.name


class ActionItemTree(object):
    def __init__(self, tree_name):
        self.name = tree_name

    def to_tuple(self):
        return defs.SA_TREE, self.name


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

if __name__ == "__main__":
    em = FsmModel()
    hello = em.add_event("hello world")
    em.add_event("lost sth")
    em.add_event("found sth")
    em.add_state("init")
    ready = em.add_state("ready")
    dead = em.add_state("dead")
    act0 = ActionItemCall("log", [(defs.PAR_BB, "tree.py"), (defs.PAR_BB, "tree.py")])
    act1 = ActionItemCall("act1", [(defs.PAR_BB, "tree.py"), (defs.PAR_BB, "tree.py")])
    dead.enter_actions.append(act0)
    dead.enter_actions.append(act1)
    act2 = ActionItemCall("act1", [(defs.PAR_BB, "tree.py"), (defs.PAR_BB, "hello")])
    dead.leave_actions.append(act2)
    em.add_edge(dead.uid, hello.uid, ready.uid)
    dumps = pickle.dumps(em)
    r = pickle.loads(dumps)
    exp = FsmModelPythonExporter(r)
    exp.export("d:/tmp/out.py")
