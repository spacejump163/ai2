# -*- encoding: utf-8 -*-
from ai2.runtime.agent import *
from ai2.runtime.mode import is_complete


if not is_complete():
    ETABLE_NAME = "__exported__"

    def enable_register4export():
        import inspect
        local = inspect.currentframe().f_back.f_locals
        local[ETABLE_NAME] = exported = []
        def register4export(stuff):
            exported.append(stuff)
            return stuff
        local["register4export"] = register4export


    class RegisterMeta(type):
        def __new__(cls, name, bases, dct):
            del dct["register4export"]
            for b in bases:
                blist = getattr(b, ETABLE_NAME, [])
                dct[ETABLE_NAME] += blist
            return type.__new__(cls, name, bases, dct)

else:
    def enable_register4export():
        import inspect
        local = inspect.currentframe().f_back.f_locals
        def register4export(stuff):
            return stuff
        local["register4export"] = register4export

    class RegisterMeta(type):
        def __new__(cls, name, bases, dct):
            del dct["register4export"]
            return type.__new__(cls, name, bases, dct)

enable_register4export()



@register4export
class ActionAgent(Agent):
    __metaclass__ = RegisterMeta

    enable_register4export()

    @register4export
    def log(self, node, msg):
        logger.info("%s:%s:%s" % (self, node,  msg))
        node.finish(True)

    @register4export
    def push_fsm(self, node, fsm_name):
        nfsm = fsm.Fsm(fsm_name)
        nfsm.push_self(self)
        node.finish(True)

    @register4export
    def push_tree(self, node, tree_name):
        c = loader.get_root_desc(tree_name)
        self.push_node(None, 0, c)
        node.finish(True)

    @register4export
    def trigger_event(self, node, event_name):
        self.fire_event(event_name)
        node.finish(True)

    @register4export
    def set_blackboard(self, node, dst_name, expression):
        val = eval(expression, None, None)
        self.set_value((defs.PAR_BB, dst_name, val))
        node.finish(True)

    @register4export
    def nop(self, node):
        logger.info("nop action called")
        node.finish(True)

    @register4export
    def nop_enter(self, node):
        logger.debug("%s:entered nop action node" % self)
        node.finish(True)

    @register4export
    def nop_leave(self, node):
        logger.debug("%s:leaving nop action node" % self)

    @register4export
    def test_action_enter(self, node, para):
        logger.debug("%s:entered test action node" % self)

        def cb(state):
            node.finish(state)
        self.blackboard[para] = (cb, True)

    @register4export
    def test_action_leave(self, node, para):
        self.blackboard[para] = False
