info = __file__


comp_assign0 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt", "cnt"),
        ),
        compile("cnt = 4", "<string>", "exec"),
        (),
    ),
    (),
    "assign"
)

not0 = (
    "NT_NOT",
    (),
    (comp_assign0,),
    "not"
)

comp_assign1 = (
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

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait"
)

seq = (
    "NT_SEQ",
    (),
    (not0, comp_assign1, wait0),
    "seq"
)

sel = (
    "NT_SEL",
    (),
    (seq, wait0),
    "select"
)

root = (
    "NT_ROOT",
    (),
    (sel,),
    "root",
)
