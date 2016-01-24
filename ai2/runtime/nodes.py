import random

import ai2.runtime.defs as defs
import ai2.runtime.loader as loader

class Node(object):
    ENTERING = "ENTERING"
    REVISITING = "REVISITING"  # for non-leaf nodes only, called when returned from a child
    FINISHING = "FINISHING"
    BLOCKING = "BLOCKING"
    WAIT_CHILD = "WAIT_CHILD"
    DEAD = "DEAD"
    READY_STATES = {ENTERING, REVISITING, FINISHING}

    __slots__ = ("desc", "state", "agent", "agent", "parent", "children", "children_states", "index")
    multiple_children = False

    def __init__(self, parent, index, node_desc, agent):
        self.desc = defs.NodeDesc(*node_desc)
        self.state = self.ENTERING
        self.agent = agent
        self.parent = parent
        self.index = index  # index in parent's children list
        self.children = {}  # needed for subtree interrupt
        if parent:
            parent.children[self] = None
        agent.fronts.add(self)

    def _quick_finish(self, retval):
        """
        this is only to be used by internal nodes other than user action nodes,
        at the end of this method, agent will be polled since
        some event may just have happened
        """
        assert(retval is True or retval is False)
        assert(self.state != self.FINISHING)
        self.state = self.FINISHING
        if self.parent:
            self.parent.children[self] = retval

    def finish(self, retval):
        self._quick_finish(retval)
        if not self.agent.processing:
            self.agent.poll()

    def block(self):
        assert(self.state == self.ENTERING)
        self.state = self.BLOCKING

    def visit(self):
        if self.state == self.ENTERING:
            self.enter()
            assert(self.state != self.ENTERING)
        elif self.state == self.FINISHING:
            self.leave()
            self.backtrace()
            assert(self.state != self.FINISHING)
        elif self.state == self.REVISITING:
            self.revisit()
            assert(self.state != self.REVISITING)
        else:
            return False
        return True

    def enter(self):
        raise NotImplemented

    def leave(self):
        pass

    def backtrace(self):
        assert(self in self.agent.fronts)
        assert(self.parent.state in {self.REVISITING, self.BLOCKING, self.WAIT_CHILD})
        self.parent.state = self.REVISITING
        self.agent.fronts.remove(self)
        self.agent.fronts.add(self.parent)
        """
        we can not delete children from parent's children because prent may
        need to collect children returned value
        #self.parent.children.pop(self)
        """
        self.state = self.DEAD

    def push_child(self, n):
        assert(
            self is None or
            self.multiple_children or
            ((not self.multiple_children) and self in self.agent.fronts))
        c = defs.NodeDesc(*self.desc.children[n])
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
        for k, v in self.children:
            v.interrupt()
        self.state = self.DEAD

    def revisit(self):
        raise NotImplemented

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
        self.push_child(0)

    def revisit(self):
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
        self.push_child(0)

    def revisit(self):
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
        idx = self.order.pop(-1)
        self.push_child(idx)

    def revisit(self):
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
        self.push_child(0)

    def revisit(self):
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
        high = self.desc.data[-1]
        rv = random.uniform(0, high)
        idx = bsearch(self.desc.data, 0, len(self.desc.data), rv)
        self.push_child(idx)

    def revisit(self):
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
        self.internal_state = self.CONDITION_EXECUTED  # condition node executed
        self.push_child(0)

    def revisit(self):
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
        n = len(self.desc.children)
        for idx in range(0, n):
            self.push_child(idx)

    def revisit(self):
        finished = []
        for k, v in self.children.items():
            if v is not None:
                finished.append((k, v))
            else:
                k.interrupt()
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
        self.internal_state = self.CHILD
        self.push_child(0)

    def revisit(self):
        if self.internal_state == self.PREDICATE:
            self.clear_children()
            self.internal_state = self.CHILD
            self.push_child(0)
        else:
            ret = self.get_single_result()
            if ret is True:
                self._quick_finish(True)
            else:
                self.internal_state = self.PREDICATE
                self.push_child(1)


class Not(Node):
    __slots__ = ()

    def enter(self):
        self.push_child(0)

    def revisit(self):
        ret = self.get_single_result()
        self._quick_finish(not ret)


class Always(Node):
    __slots__ = ()

    def enter(self):
        self.push_child(0)

    def revisit(self):
        self._quick_finish(self.desc.data)


class Call(Node):
    __slots__ = ()

    def enter(self):
        tree_name = self.desc.data
        c = loader.get_root_desc(tree_name)
        self.wait_for_child()
        self.agent.push_node(self, 0, c)

    def revisit(self):
        ret = self.get_single_result()
        self._quick_finish(ret)


class Action(Node):
    __slots__ = ()

    def enter(self):
        self.block()  # this is the default action
        action_name = self.desc.data[0][0]
        action_args = self.desc.data[0][1:]
        self.agent.agent_action(self, action_name, action_args)

    def leave(self):
        action_name = self.desc.data[1][0]
        action_args = self.desc.data[1][1:]
        self.agent.agent_action(self, action_name, action_args)


class Compute(Node):
    __slots__ = ()

    def enter(self):
        oargs = self.desc.data[2]
        func = self.desc.data[0]
        iargs = self.desc.data[1]
        self.agent.execute(oargs, func, iargs)
        self._quick_finish(True)


class Condition(Node):
    __slots__ = ()

    def enter(self):
        func = self.desc.data[0]
        iargs = self.desc.data[1]
        r = self.agent.evaluate(func, iargs)
        assert(r is True or r is False)
        self._quick_finish(bool(r))


class WaitFor(Node):
    __slots__ = ()

    def enter(self):
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
    i = bsearch(a, 0, len(a), 0)
    print(i)

    a = (1, 2, 3, 4)
    i = bsearch(a, 0, len(a), 1)
    print(i)

    a = (1, 2, 3, 4)
    i = bsearch(a, 0, len(a), 1.1)
    print(i)

    a = (1, 2, 3, 4)
    i = bsearch(a, 0, len(a), 2)
    print(i)

    a = (1, 2, 3, 4)
    i = bsearch(a, 0, len(a), 2.2)
    print(i)

    a = (1, 2, 3, 4)
    i = bsearch(a, 0, len(a), 3)
    print(i)
