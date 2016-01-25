import sys
import logging

import ai2.runtime.loader as loader
import ai2.runtime.agent as agent

logger = logging.getLogger("ai")


def state_machine0():
    """
    this test 1 level state and fire_event triggered state transition
    """
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("state_machine_test.two_states_fsm")
    ta.enable(True)
    assert(ta.blackboard["current_state"]) == "start"
    logger.debug("event e")
    ta.fire_event("e")
    assert(ta.blackboard["current_state"]) == "end"
    logger.debug("event s")
    ta.fire_event("s")
    assert(ta.blackboard["current_state"]) == "start"
    logger.debug("event t")
    ta.fire_event("t")
    assert(ta.blackboard["current_state"]) == "end"


def state_machine1():
    """
    this test multi level states and state transition
    """
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("state_machine_test.lv0_fsm")
    ta.enable(True)
    assert(ta.blackboard["state"]) == "s00"
    ta.fire_event("e1")
    assert(ta.blackboard["state"]) == "s10"
    ta.fire_event("e3")
    assert(ta.blackboard["state"]) == "s11"
    ta.fire_event("e2")
    assert(ta.blackboard["state"]) == "s02"
    ta.fire_event("e2")
    assert(ta.blackboard["state"]) == "s02"


def sequence0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.blackboard["test_tree"] = "sequence_test.sequence_test0_btree"
    ta.set_fsm("common.simple_fsm")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 13)
    assert(ta.blackboard["count1"] == 14)


def sequence1():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.blackboard["test_tree"] = "sequence_test.sequence_test1_btree"
    ta.set_fsm("common.simple_fsm")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 1)
    assert(ta.blackboard["count1"] == 2)


def random_sequence0():
    logger.debug(">>>>")
    results = set()
    for i in range(0, 100):
        ta = agent.ActionAgent()
        ta.set_fsm("common.simple_fsm")
        ta.blackboard["test_tree"] = "random_sequence_test.random_sequence_test_btree"
        ta.enable(True)
        results.add(ta.blackboard["ret"])
    logger.debug("WARNING: this is not a strict test and you have to be very unlucky not to pass it")
    assert(len(results) == 6)


def select0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "select_test.select_test0_btree"
    ta.enable(True)
    assert(ta.blackboard["count0"] == 13)
    assert(ta.blackboard["count1"] == 14)


def select1():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "select_test.select_test1_btree"
    ta.enable(True)
    assert(ta.blackboard["count0"] == 1)
    assert(ta.blackboard["count1"] == 2)

def probability0():
    logger.debug(">>>>")
    results = {0:0, 1:0, 2:0}
    for i in range(0, 100):
        ta = agent.ActionAgent()
        ta.set_fsm("common.simple_fsm")
        ta.blackboard["test_tree"] = "probability_test.probability_test_btree"
        ta.enable(True)
        k = ta.blackboard["ret"]
        results[k] += 1
    logger.debug("WARNING: this is not a strict test and you have to be very unlucky not to pass it")
    assert(results[0] < results[1])
    assert(results[1] < results[2])

def ifelse0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "if_else_test.if_else_test0_btree"
    ta.enable(True)
    assert(ta.blackboard["ret"] == 0)

def ifelse1():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "if_else_test.if_else_test1_btree"
    ta.enable(True)
    assert(ta.blackboard["ret"] == 1)

def ifelse2():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "if_else_test.if_else_test2_btree"
    ta.blackboard["tv"] = 2
    ta.enable(True)
    assert(ta.blackboard["ret"] == 0)
    ta.blackboard["tv"] = 0
    ta.fire_event("goon")
    assert(ta.blackboard["ret"] == 1)

def parallel0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "parallel_test.parallel_test0_btree"
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.fire_event("timeout")
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)

def parallel1():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "parallel_test.parallel_test1_btree"
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.blackboard[22][0](False)
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)
    ta.fire_event("timeout")

def parallel2():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "parallel_test.parallel_test2_btree"
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.blackboard[22][0](True)
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)
    ta.fire_event("timeout")

def until0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "until_test.until_test_btree"
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 4)

def not0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "not_test.not_test_btree"
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 0)

def always0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "always_test.always_test0_btree"
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 4)

def always1():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "always_test.always_test1_btree"
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 1)

def call0():
    logger.debug(">>>>")
    ta = agent.ActionAgent()
    ta.set_fsm("common.simple_fsm")
    ta.blackboard["test_tree"] = "call_test.call_test0_btree"
    ta.enable(True)
    assert(ta.blackboard["cnt0"] == 2)
    assert(ta.blackboard["cnt1"] == 4)


def run():
    logging.basicConfig(level=logging.DEBUG)
    loader.prefix = "ai2.test."

    state_machine0()
    state_machine1()

    sequence0()
    sequence1()

    random_sequence0()

    select0()
    select1()

    probability0()

    ifelse0()
    ifelse1()
    ifelse2()

    parallel0()
    parallel1()
    parallel2()

    until0()

    not0()

    always0()
    always1()
    call0()
    logger.debug(">>> finished")
    return
