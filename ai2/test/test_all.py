import sys
import logging

import ai2.runtime.loader as loader
import ai2.runtime.agent as agent

logger = logging.getLogger("ai")


def sequence0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("sequence_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 13)
    assert(ta.blackboard["count1"] == 14)


def sequence1():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("sequence_test.fsm1")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 1)
    assert(ta.blackboard["count1"] == 2)


def random_sequence0():
    logger.debug(">>>>")
    results = set()
    for i in range(0, 1000):
        ta = agent.Agent()
        ta.set_fsm("random_sequence_test.fsm0")
        ta.enable(True)
        results.add(ta.blackboard["ret"])
    logger.debug("WARNING: this is not a strict test and you have to be very unlucky not to pass it")
    assert(len(results) == 6)


def select0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("select_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 13)
    assert(ta.blackboard["count1"] == 14)


def select1():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("select_test.fsm1")
    ta.enable(True)
    assert(ta.blackboard["count0"] == 1)
    assert(ta.blackboard["count1"] == 2)

def probability0():
    logger.debug(">>>>")
    results = {0:0, 1:0, 2:0}
    for i in range(0, 1000):
        ta = agent.Agent()
        ta.set_fsm("probability_test.fsm0")
        ta.enable(True)
        k = ta.blackboard["ret"]
        results[k] += 1
    logger.debug("WARNING: this is not a strict test and you have to be very unlucky not to pass it")
    assert(results[0] < results[1])
    assert(results[1] < results[2])

def ifelse0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("if_else_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["ret"] == 0)

def ifelse1():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("if_else_test.fsm1")
    ta.enable(True)
    assert(ta.blackboard["ret"] == 1)

def parallel0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("parallel_test.fsm0")
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.fire_event("timeout")
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)

def parallel1():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("parallel_test.fsm0")
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.blackboard[22][0](True)
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)
    ta.fire_event("timeout")

def parallel2():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("parallel_test.fsm1")
    ta.enable(True)

    assert(ta.blackboard[22][1] == True)
    assert(ta.blackboard[33][1] == True)
    assert(ta.is_ready() == False)

    ta.blackboard[22][0](False)
    assert(ta.blackboard[22] is False)
    assert(ta.blackboard[33] is False)
    ta.fire_event("timeout")

def until0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("until_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 4)

def not0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("not_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 4)

def always0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("always_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 4)

def always1():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("always_test.fsm1")
    ta.enable(True)
    assert(ta.blackboard["cnt"] == 1)

def call0():
    logger.debug(">>>>")
    ta = agent.Agent()
    ta.set_fsm("call_test.fsm0")
    ta.enable(True)
    assert(ta.blackboard["cnt0"] == 2)
    assert(ta.blackboard["cnt1"] == 4)


def test_all():
    logging.basicConfig(level=logging.WARNING)
    loader.prefix = "ai2.test."
    sequence0()
    sequence1()

    random_sequence0()

    select0()
    select1()

    probability0()

    ifelse0()
    ifelse1()

    parallel0()
    parallel1()
    parallel2()

    until0()

    not0()

    always0()
    always1()

    call0()

    #assert(False)
    logger.debug(">>> finished")
