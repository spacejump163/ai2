from collections import namedtuple

# fsm def
# enumerates
SA_GRAPH = "SA_GRAPH"  # push graph
SA_TREE = "SA_TREE"  # start a new behavior tree
SA_CALL = "SA_CALL"  # call function

PAR_CONST = "PAR_CONST"  # const parameter
PAR_BB = "PAR_BB"  # blackboard parameter
PAR_PROP = "PAR_PROP"  # property parameter

# types
StateDesc = namedtuple("StateDesc", ("enter_actions", "leave_actions", "debug_info"))

# btree def
# enumerates
NT_ROOT = "NT_ROOT"
NT_SEQ = "NT_SEQ"
NT_RSEQ = "NT_RSEQ"
NT_SEL = "NT_SEL"
NT_PSEL = "NT_PSEL"
NT_IF = "NT_IF"
NT_PARL = "NT_PARL"
NT_UNTIL = "NT_UNTIL"
NT_NOT = "NT_NOT"
NT_TRUE = "NT_TRUE"
NT_ALWAYS = "NT_ALWAYS"
NT_CALL = "NT_CALL"

NT_ACT = "NT_ACT"
NT_COMP = "NT_COMP"
NT_COND = "NT_COND"
NT_WAIT = "NT_WAIT"

# types
NodeDesc = namedtuple("NodeDesc", ("category", "data", "children", "debug_info"))
