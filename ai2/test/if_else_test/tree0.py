info = __file__


comp0 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "ret", "ret"),
        ),
        compile("ret = 0", "<string>", "exec"),
        (),
    ),
    (),
    "compute0"
)

comp1 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "ret", "ret"),
        ),
        compile("ret = 1", "<string>", "exec"),
        (),
    ),
    (),
    "compute0"
)

cond0 = (
    "NT_COND",
    (
        compile("True", "<string>", "eval"),
        (),
    ),
    (),
    "condition",
)


prob = (
    "NT_IF",
    (),
    (cond0, comp0, comp1),
    "random sequence"
)

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait0",
)

seq0 = (
    "NT_SEQ",
    (),
    (prob, wait0),
    "select0"
)

root = (
    "NT_ROOT",
    (),
    (seq0,),
    "root",
)
