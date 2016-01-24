import logging
import collections

import ai2.runtime.fsm as fsm
import ai2.runtime.nodes as nodes
import ai2.runtime.defs as defs
import ai2.runtime.loader as loader

logger = logging.getLogger("ai")


class Agent(object):
    def __init__(self):
        super(Agent, self).__init__()

        # ai state variables
        self._enabled = False
        self.processing = False  # whether the agent is being processed(processing events and walking btree)

        # event queue
        self.event_queue = collections.deque()
        # fsm stack related
        self.fsm_name = None
        self.fsm_stack = []

        # behavior tree related
        self.btree = None
        self.fronts = set()

        # blackboard
        self.blackboard = {}

    def enable(self, on_off):
        """
        ai execution will be triggered during this call
        :param on_off: should be AI be enabled or not
        :return: None
        """
        if self._enabled == on_off:
            return
        elif on_off:
            self._start()
        else:
            self._stop()

    def fire_event(self, event):
        """
        ai execution will be triggered during this call
        :param event: event to be received
        :return: None
        """
        if not self._enabled:
            return
        self.event_queue.append(event)
        if not self.processing:
            self.poll()

    def _btree_check_event(self, event):
        for n in self.fronts:
            ret = n.try_swallow(event)
            if ret:
                return True
        return False

    def _fsm_check_event(self, event):
        swallowed, new_state_index = False, None
        if swallowed:
            return True
        receiver = None
        tail = len(self.fsm_stack) - 1
        head = tail
        for f in reversed(self.fsm_stack):
            swallowed, new_state_index = f.try_receive_event(event)
            if swallowed:
                receiver = f
                break
            else:
                head -= 1
        if receiver is None:
            return False
        for fsmi in range(tail, head, -1):
            f = self.fsm_stack[fsmi]
            f.pop_self()
        receiver.transfer_state(new_state_index)
        return True

    def set_fsm(self, fsm_name):
        self.fsm_name = fsm_name

    @staticmethod
    def enable_debug(self):
        raise NotImplemented

    def agent_action(self, node, method_name, arg_list):
        if method_name == "":
            return
        f = getattr(self, method_name)
        args = [self.get_value(i) for i in arg_list]
        return f(node, *args)

    def get_value(self, tup):
        if tup[0] == defs.PAR_CONST:
            return tup[1]
        elif tup[0] == defs.PAR_BB:
            return self.blackboard[tup[1]]
        elif tup[0] == defs.PAR_PROP:
            return getattr(self, tup[1])
        else:
            assert False

    def set_value(self, tup):
        if tup[0] == defs.PAR_BB:
            self.blackboard[tup[1]] = tup[2]
        elif tup[0] == defs.PAR_PROP:
            setattr(self, tup[1], tup[2])
        else:
            assert False

    def _start(self):
        self._enabled = True
        # stack should be empty
        assert(len(self.fsm_stack) == 0)
        nfsm = fsm.Fsm(self.fsm_name)
        nfsm.push_self(self)
        self.poll()

    def _stop(self):
        self._enabled = False
        raise NotImplemented

    def is_ready(self):
        for n in self.fronts:
            if n.state == n.BLOCKING:
                pass
            else:
                assert(n.state in n.READY_STATES)
                return True
        return len(self.event_queue)

    def execute(self, dst, formula, src):
        local = {}
        for tp, var_name, expr_name in src:
            local[expr_name] = self.get_value((tp, var_name))
        exec(formula, {}, local)
        for tp, var_name, expr_name in dst:
            self.set_value((tp, var_name, local[expr_name]))

    def evaluate(self, formula, src):
        local = {}
        for tp, var_name, expr_name in src:
            local[expr_name] = self.get_value((tp, var_name))
        r = eval(formula, {}, local)
        return r

    def push_node(self, parent, child_index, node_desc):
        clz = nodes.get_node_class(node_desc[0])
        clz(parent, child_index, node_desc, self)

    def poll_fronts(self):
        need_process = False
        for n in self.fronts:
            if n.state != n.BLOCKING:
                assert(n.state in n.READY_STATES)
                need_process = True
                break
        if not need_process:
            return False
        # note that self.front will change during iteration
        # process each front until all fronts are blocking
        assert(self.processing is False)
        self.processing = True
        has_ready = True
        while has_ready:
            has_ready = False
            visit_set = set(self.fronts)
            for n in visit_set:
                # note that when parallel return, some node in visit_set
                # will become DEAD before visited
                if n.state != n.BLOCKING and n.state != n.DEAD:
                    has_ready = True
                    assert(n.state in n.READY_STATES)
                    n.visit()
        self.processing = False
        return True  # processed something

    def poll_events(self):
        assert(self.processing is False)
        self.processing = True
        processed = False
        while len(self.event_queue):
            event = self.event_queue.popleft()
            ret = self._btree_check_event(event)
            if ret:
                processed = True
                break
            ret = self._fsm_check_event(event)
            if not ret:
                logger.info("event with no receiver:%s" % event)
            processed = True
        self.processing = False
        return processed

    def poll(self):
        while True:
            ret0 = self.poll_events()
            ret1 = self.poll_fronts()
            if ret0 is False and ret1 is False:
                break


class ActionAgent(Agent):
    def log(self, node, msg):
        logger.debug("%s:%s:%s" % (self, node,  msg))
        node.finish(True)

    def push_fsm(self, node, fsm_name):
        nfsm = fsm.Fsm(fsm_name)
        nfsm.push_self(self)

    def push_tree(self, node, tree_name):
        c = loader.get_root_desc(tree_name)
        self.push_node(None, 0, c)

    def set_blackboard(self, node, dst_name, expression):
        val = eval(expression, None, None)
        self.set_value((defs.PAR_BB, dst_name, val))

    def nop(self, node):
        logger.info("nop action called")

    def nop_enter(self, node):
        logger.debug("%s:entered nop action node" % self)
        node.finish(True)

    def nop_leave(self, node):
        logger.debug("%s:leaving nop action node" % self)

    def test_action_enter(self, node, para):
        logger.debug("%s:entered test action node" % self)

        def cb(state):
            node.finish(state)
        self.blackboard[para] = (cb, True)

    def test_action_leave(self, node, para):
        self.blackboard[para] = False


    to_export = (
        log, push_fsm, push_tree, set_blackboard,
        nop_enter, nop_leave,
        test_action_enter, test_action_leave,
    )

to_export = {ActionAgent}