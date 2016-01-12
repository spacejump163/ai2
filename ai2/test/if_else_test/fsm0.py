info = __file__

states = [
    (
        (
            ("SA_CALL", "log", ("PAR_CONST", "entered fsm0:s0")),
            ("SA_CALL", "log", ("PAR_CONST", "transfer tree0")),
            ("SA_TREE", "if_else_test.tree0"),
        ),
        (
            ("SA_CALL", "log", ("PAR_CONST", "leaving fsm0:s0")),
        ),
        "s0"
    ),
]
initial_state_index = 0
events = []

graph = {
}