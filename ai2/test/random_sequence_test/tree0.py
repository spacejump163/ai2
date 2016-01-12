info = __file__


comp0 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "ret", "ret"),
        ),
        compile("ret = ''", "<string>", "exec"),
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
        compile("ret = '1' + ret", "<string>", "exec"),
        (
            ("PAR_BB", "ret", "ret"),
        ),
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
        compile("ret = '2' + ret", "<string>", "exec"),
        (
            ("PAR_BB", "ret", "ret"),
        ),
    ),
    (),
    "compute0"
)

comp3 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "ret", "ret"),
        ),
        compile("ret = '3' + ret", "<string>", "exec"),
        (
            ("PAR_BB", "ret", "ret"),
        ),
    ),
    (),
    "compute0"
)

rseq = (
    "NT_RSEQ",
    (),
    (comp1, comp2, comp3),
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
    (comp0, rseq, wait0),
    "select0"
)

root = (
    "NT_ROOT",
    (),
    (seq0,),
    "root",
)
