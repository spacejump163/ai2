info = __file__


comp_assign0 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
        compile("cnt = 1", "<string>", "exec"),
        (),
    ),
    (),
    "assign"
)

always0 = (
    "NT_ALWAYS",
    True,
    (comp_assign0,),
    "not"
)

comp_assign1 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
        compile("cnt = 2", "<string>", "exec"),
        (),
    ),
    (),
    "assign"
)

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait"
)

sel0 = (
    "NT_SEL",
    (),
    (always0, comp_assign1, wait0),
    "sel"
)

seq = (
    "NT_SEQ",
    (),
    (sel0, wait0),
    "seq"
)

root = (
    "NT_ROOT",
    (),
    (seq,),
    "root",
)
