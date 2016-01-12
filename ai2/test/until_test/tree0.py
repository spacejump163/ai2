info = __file__


comp_assign = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
        compile("cnt = 0", "<string>", "exec"),
        (),
    ),
    (),
    "assign"
)

comp_inc = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
        compile("cnt += 1", "<string>", "exec"),
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
    ),
    (),
    "assign 0"
)

cond0 = (
    "NT_COND",
    (
        compile("cnt == 4", "<string>", "eval"),
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
    ),
    (),
    "check"
)

until0 = (
    "NT_UNTIL",
    (),
    (cond0, comp_inc),
    "until"
)

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait"
)

seq = (
    "NT_SEQ",
    (),
    (comp_assign, until0, wait0),
    "seq"
)

root = (
    "NT_ROOT",
    (),
    (seq,),
    "root",
)
