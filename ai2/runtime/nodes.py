# -*- encoding: utf-8 -*-
import random
import logging

import ai2.runtime.defs as defs
import ai2.runtime.loader as loader

logger = logging.getLogger(__name__)


class Node(object):
    NEW = "NEW"
    ENTERING = "ENTERING"
    AWAKEN = "AWAKEN"
    REVISITING = "REVISITING"
    BLOCKING = "BLOCKING"
    WAIT_CHILD = "WAIT_CHILD"
    LEAVING = "LEAVING"
    DEAD = "DEAD"
    # leaving should not be ready_state because it would be processed instantly
    # i.e. no poll loop
    READY_STATES = {NEW, AWAKEN}
    DEBUG_STATES = {
        ENTERING, AWAKEN, REVISITING, BLOCKING,
        WAIT_CHILD, LEAVING, DEAD}

    __slots__ = ("desc", "_state", "agent", "parent", "children", "children_states", "index")
    multiple_children = False

    def __repr__(self):
        return repr(self.desc.debug_info)

    def __init__(self, parent, index, node_desc, agent):
        self.desc = defs.NodeDesc(*node_desc)
        self._state = self.NEW
        self.agent = agent
        self.parent = parent
        self.index = index  # index in parent's children list
        self.children = {}  # needed for subtree interrupt
        if parent:
            parent.children[self] = None
        agent.fronts.add(self)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value in self.DEBUG_STATES:
            self._state = value
            if self.agent.debugger:
                self.agent.debugger.check_debug(self)

    def _quick_finish(self, retval):
        """
        this is only to be used by internal nodes other than user action nodes,
        at the end of this method, agent will be polled since
        some event may just have happened
        """
        # retval is be nothing else
        # logger.info("%s finished with %s" % (self, retval))
        assert retval is True or retval is False, retval
        # _quick_finish can only be called when node is not dead because
        # after this it will be dead
        assert self.state != self.DEAD, self.state
        if self.parent:
            self.parent.children[self] = retval
            # node state would be leaving when called self.leave()
            self.leave()
            # node state would be DEAD after backtrace
            self.backtrace()

    def finish(self, retval):
        if self.state == self.DEAD:
            # this saves a lot of trouble but somehow hide errors
            return
        self._quick_finish(retval)
        if not self.agent.processing:
            self.agent.poll()

    def block(self):
        # this is only for action node, not for composition nodes
        # can only block on entering
        assert self.state == self.ENTERING, self.state
        self.state = self.BLOCKING

    def visit(self):
        # logger.info("%s, %s" %(self, self.state))
        if self.state == self.NEW:
            self.enter()
            # can only be block, finishing
            assert self.state != self.ENTERING, self.state
        elif self.state == self.AWAKEN:
            self.revisit()
            assert self.state != self.REVISITING, self.state
        else:
            return False
        return True

    def enter(self):
        self.state = self.ENTERING

    def leave(self):
        self.state = self.LEAVING

    def backtrace(self):
        # parent should still be valid and waiting
        assert self in self.agent.fronts, (self, self.agent.fronts)
        assert self.parent.state in {self.AWAKEN, self.WAIT_CHILD}, self.parent.state
        self.agent.fronts.remove(self)
        self.state = self.DEAD
        self.agent.fronts.add(self.parent)
        self.parent.state = self.AWAKEN
        """
        we can not delete children from parent's children because parent may
        need to collect children returned value
        #self.parent.children.pop(self)
        """

    def push_child(self, n):
        assert self in self.agent.fronts, self.state
        c = defs.NodeDesc(*self.desc.children[n])
        if not self.multiple_children:
            self.wait_for_child()
        self.agent.push_node(self, n, c)

    def wait_for_child(self):
        if self in self.agent.fronts:
            self.agent.fronts.remove(self)
        self.state = self.WAIT_CHILD

    def interrupt(self):
        # interrupt a subtree
        # note that interrupt leaves btree in an unstable state since agent.fronts is not valid
        self.leave()
        if self in self.agent.fronts:
            self.agent.fronts.remove(self)
        for k in self.children:
            k.interrupt()
        self.state = self.DEAD

    def revisit(self):
        self.state = self.REVISITING

    def clear_children(self):
        self.children.clear()

    def get_single_result(self):
        assert(len(self.children) == 1)
        for v in self.children.values():
            return v

    def is_waiting_for(self, event):
        return False

    def try_swallow(self, event):
        ret = self.is_waiting_for(event)
        if ret:
            self._quick_finish(True)
            return True
        else:
            return False

    def get_location_info(self):
        return self.desc.debug_info, self.state


class Root(Node):
    """
    real root node never end, intermediate root(called tree) do nothing
    """
    __slots__ = ()

    def __init__(self, parent, index, node_desc, agent):
        if parent is None:
            agent.btree = self
        super(Root, self).__init__(parent, index, node_desc, agent)

    def enter(self):
        super(Root, self).enter()
        self.push_child(0)

    def revisit(self):
        super(Root, self).revisit()
        is_real_root = self.parent is None
        if is_real_root:
            self.clear_children()
            self.push_child(0)
        else:
            ret = self.get_single_result()
            self._quick_finish(ret)


class Sequence(Node):
    __slots__ = ("cur_cidx",)

    def __init__(self, *args, **kwargs):
        self.cur_cidx = 0
        super(Sequence, self).__init__(*args, **kwargs)

    def enter(self):
        super(Sequence, self).enter()
        self.push_child(0)

    def revisit(self):
        super(Sequence, self).revisit()
        # check result
        ret = self.get_single_result()
        if ret is False:
            self._quick_finish(False)
            return
        self.cur_cidx += 1
        if self.cur_cidx == len(self.desc.children):
            self._quick_finish(True)
            return
        self.clear_children()
        self.push_child(self.cur_cidx)


class RandomSequence(Node):
    __slots__ = ("order",)

    def __init__(self, parent, index, node_desc, agent):
        n = len(defs.NodeDesc(*node_desc).children)
        self.order = [i for i in range(0, n)]
        random.shuffle(self.order)
        super(RandomSequence, self).__init__(parent, index, node_desc, agent)

    def enter(self):
        super(RandomSequence, self).enter()
        idx = self.order.pop(-1)
        self.push_child(idx)

    def revisit(self):
        super(RandomSequence, self).revisit()
        ret = self.get_single_result()
        if ret is False:
            self._quick_finish(False)
            return
        if len(self.order) == 0:
            self._quick_finish(True)
            return
        self.clear_children()
        idx = self.order.pop(-1)
        self.push_child(idx)


class Select(Node):
    __slots__ = ("cur_cidx",)

    def __init__(self, *args, **kwargs):
        self.cur_cidx = 0
        super(Select, self).__init__(*args, **kwargs)

    def enter(self):
        super(Select, self).enter()
        self.push_child(0)

    def revisit(self):
        super(Select, self).revisit()
        # check result
        ret = self.get_single_result()
        if ret is True:
            self._quick_finish(True)
            return
        self.cur_cidx += 1
        if self.cur_cidx == len(self.desc.children):
            self._quick_finish(False)
            return
        self.clear_children()
        self.push_child(self.cur_cidx)


def bsearch(d, b, e, v):
    while b < e:
        m = int((b + e) / 2)
        mv = d[m]
        if mv < v:
            b = m + 1
        else:
            e = m
    return b


class Probability(Node):
    __slots__ = ()

    def enter(self):
        super(Probability, self).enter()
        high = self.desc.data[-1]
        rv = random.uniform(0, high)
        idx = bsearch(self.desc.data, 0, len(self.desc.data), rv)
        self.push_child(idx)

    def revisit(self):
        super(Probability, self).revisit()
        ret = self.get_single_result()
        self._quick_finish(ret)


class IfElse(Node):
    FRESH = 0
    CONDITION_EXECUTED = 1
    BRANCH_EXECUTED = 2

    __slots__ = ("internal_state",)

    def __init__(self, *args, **kwargs):
        self.internal_state = self.FRESH  # condition node not executed
        super(IfElse, self).__init__(*args, **kwargs)

    def enter(self):
        super(IfElse, self).enter()
        self.internal_state = self.CONDITION_EXECUTED  # condition node executed
        self.push_child(0)

    def revisit(self):
        super(IfElse, self).revisit()
        if self.internal_state == self.CONDITION_EXECUTED:
            self.internal_state = self.BRANCH_EXECUTED  # branch node executed
            ret = self.get_single_result()
            self.clear_children()
            if ret is True:
                self.push_child(1)
            else:
                self.push_child(2)
        elif self.internal_state == self.BRANCH_EXECUTED:
            ret = self.get_single_result()
            self._quick_finish(ret)
        else:
            assert False


class Parallel(Node):
    multiple_children = True
    __slots__ = ()

    def enter(self):
        super(Parallel, self).enter()
        n = len(self.desc.children)
        for idx in range(0, n):
            self.push_child(idx)
        self.wait_for_child()

    def revisit(self):
        super(Parallel, self).revisit()
        finished = []
        for k, v in self.children.items():
            if v is not None:
                finished.append((k, v))
            else:
                k.interrupt()
        assert len(finished) > 0
        retval = finished[0][1]  # choose any(in most cases there should be only 1)
        if self not in self.agent.fronts:
            # manually put self back on front since interrupt do not do this
            self.agent.fronts.add(self)
        self._quick_finish(retval)


class Until(Node):
    """
    while predicate return True:
        run child
    """
    PREDICATE = 0
    CHILD = 1
    __slots__ = ("internal_state",)

    def __init__(self, *args, **kwargs):
        self.internal_state = self.PREDICATE  # should
        super(Until, self).__init__(*args, **kwargs)

    def enter(self):
        super(Until, self).enter()
        # do predicate check first
        self.push_child(0)

    def revisit(self):
        super(Until, self).revisit()
        if self.internal_state == self.PREDICATE:
            # predicate node returned, check it
            ret = self.get_single_result()
            if ret is True:
                self._quick_finish(True)
            else:
                self.internal_state = self.CHILD
                self.push_child(1)
        else:
            # action node finished, the result does not matter
            self.clear_children()
            self.internal_state = self.PREDICATE
            self.push_child(0)


class Not(Node):
    __slots__ = ()

    def enter(self):
        super(Not, self).enter()
        self.push_child(0)

    def revisit(self):
        super(Not, self).revisit()
        ret = self.get_single_result()
        self._quick_finish(not ret)


class Always(Node):
    __slots__ = ()

    def enter(self):
        super(Always, self).enter()
        self.push_child(0)

    def revisit(self):
        super(Always, self).revisit()
        self._quick_finish(self.desc.data)


class Call(Node):
    __slots__ = ()

    def enter(self):
        super(Call, self).enter()
        tree_name = self.desc.data
        c = loader.get_root_desc(tree_name)
        self.wait_for_child()
        self.agent.push_node(self, 0, c)

    def revisit(self):
        super(Call, self).revisit()
        ret = self.get_single_result()
        self._quick_finish(ret)


class Action(Node):
    __slots__ = ("node_state",)

    def enter(self):
        super(Action, self).enter()
        action_name = self.desc.data[0][0]
        action_args = self.desc.data[0][1:]
        self.agent.agent_action(self, action_name, action_args)
        if self.state == self.ENTERING:
            self.block()  # this is the default action

    def leave(self):
        super(Action, self).leave()
        action_name = self.desc.data[1][0]
        action_args = self.desc.data[1][1:]
        self.agent.agent_action(self, action_name, action_args)


class Compute(Node):
    __slots__ = ()

    def enter(self):
        super(Compute, self).enter()
        oargs = self.desc.data[2]
        func = self.desc.data[0]
        iargs = self.desc.data[1]
        self.agent.execute(oargs, func, iargs)
        self._quick_finish(True)


class Condition(Node):
    __slots__ = ()

    def enter(self):
        super(Condition, self).enter()
        func = self.desc.data[0]
        iargs = self.desc.data[1]
        r = self.agent.evaluate(func, iargs)
        assert(r is True or r is False)
        self._quick_finish(bool(r))


class WaitFor(Node):
    __slots__ = ()

    def enter(self):
        super(WaitFor, self).enter()
        self.block()

    def is_waiting_for(self, event):
        desired_event = self.desc.data
        return event == desired_event


_type_to_class = {
    defs.NT_ROOT: Root,
    defs.NT_SEQ: Sequence,
    defs.NT_RSEQ: RandomSequence,
    defs.NT_SEL: Select,
    defs.NT_PSEL: Probability,
    defs.NT_IF: IfElse,
    defs.NT_PARL: Parallel,
    defs.NT_UNTIL: Until,
    defs.NT_NOT: Not,
    defs.NT_ALWAYS: Always,
    defs.NT_CALL: Call,
    defs.NT_ACT: Action,
    defs.NT_COMP: Compute,
    defs.NT_COND: Condition,
    defs.NT_WAIT: WaitFor,

}


def get_node_class(node_type):
    return _type_to_class[node_type]


if __name__ == "__main__":
    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 0)
    print(ii)

    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 1)
    print(ii)

    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 1.1)
    print(ii)

    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 2)
    print(ii)

    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 2.2)
    print(ii)

    a = (1, 2, 3, 4)
    ii = bsearch(a, 0, len(a), 3)
    print(ii)
