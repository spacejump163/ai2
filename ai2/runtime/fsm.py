import logging

import ai2.runtime.defs as defs
import ai2.runtime.loader as loader

logger = logging.getLogger("ai.fsm")


class Fsm(object):
    def __init__(self, fsm_desc_name):
        self.desc = loader.load_fsm(fsm_desc_name)
        self.agent = None
        self.current_state_index = None
        self.info = self.desc.info

    def push_self(self, agent):
        # bound agent
        self.agent = agent
        self.agent.fsm_stack.append(self)
        # enter initial state
        self._enter_state(self.desc.initial_state_index)

    def try_receive_event(self, event):
        """
        an event can be received/swallowed by a state machine if
        (current_state, event) tuple is in graph
        :param event: event identifier
        :return: bool, int -> receivable, new state index
        """
        try:
            event_index = self.desc.events.index(event)
            key = (self.current_state_index, event_index)
            if key in self.desc.graph:
                return True, self.desc.graph[key]
            else:
                return False, None
        except ValueError:
            return False, None

    def pop_self(self):
        self._leave_state()
        assert(self.agent.fsm_stack[-1] is self)
        self.agent.fsm_stack.pop(-1)
        self.agent = None

    def _enter_state(self, state_index):
        self.current_state_index = state_index
        nstate = defs.StateDesc(*self.desc.states[self.current_state_index])
        enter_actions = nstate.enter_actions  # enter state actions
        for a in enter_actions:
            if a[0] == defs.SA_GRAPH:
                nfsm = Fsm(a[1])
                nfsm.push_self(self.agent)  # recursively
            elif a[0] == defs.SA_TREE:
                c = loader.get_root_desc(a[1])
                self.agent.push_node(None, 0, c)
            elif a[0] == defs.SA_CALL:
                self.agent.fsm_action(a[1], a[2:])
            else:
                assert(False)

    def _leave_state(self, state_index=None):
        if self.agent.btree is not None:
            self.agent.btree.interrupt()
            self.agent.btree = None
        if state_index is None:
            state_index = self.current_state_index
        cstate = defs.StateDesc(*self.desc.states[state_index])
        leave_actions = cstate.leave_actions
        for a in leave_actions:
            assert(a[0] == defs.SA_CALL)
            self.agent.action(a[1], a[2:])
        self.current_state_index = None

    def transfer_state(self, state_index):
        self._leave_state()
        self._enter_state(state_index)
