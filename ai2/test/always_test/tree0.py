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

always0 = (
    "NT_ALWAYS",
    False,
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
    (always0, comp_assign1, wait0),
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
