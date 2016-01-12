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

comp2 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "ret", "ret"),
        ),
        compile("ret = 2", "<string>", "exec"),
        (),
    ),
    (),
    "compute0"
)


prob = (
    "NT_PSEL",
    (10, 30, 60),
    (comp0, comp1, comp2),
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
