info = __file__


comp_false = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "test_action_in", "ret"),
        ),
        compile("ret = False", "<string>", "exec"),
        (),
    ),
    (),
    "compute0"
)

comp_true = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "test_action_in", "ret"),
        ),
        compile("ret = True", "<string>", "exec"),
        (),
    ),
    (),
    "compute0"
)

act0 = (
    "NT_ACT",
    (
        ("test_action_enter", ("PAR_CONST", 22)),
        ("test_action_leave", ("PAR_CONST", 22)),
    ),
    (),
    "action",
)

act1 = (
    "NT_ACT",
    (
        ("test_action_enter", ("PAR_CONST", 33)),
        ("test_action_leave", ("PAR_CONST", 33)),
    ),
    (),
    "action",
)

wait_tmout = (
    "NT_WAIT",
    "timeout",
    (),
    "wait_timeout"
)

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait"
)

parallel0 = (
    "NT_PARL",
    (),
    (act0, act1, wait_tmout),
    "parallel"
)

sel = (
    "NT_SEL",
    (),
    (parallel0, wait0),
    "seq"
)

root = (
    "NT_ROOT",
    (),
    (sel,),
    "root",
)
