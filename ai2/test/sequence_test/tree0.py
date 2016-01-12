info = __file__

nop0 = (
    "NT_ACT",
    (
        ("nop_enter",),
    ),
    (),
    "nop",
)
always0 = (
    "NT_ALWAYS",
    True,
    (nop0,),
    "always0",
)

always1 = (
    "NT_ALWAYS",
    True,
    (nop0,),
    "always1",
)

compute0 = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "count0", "count0"),
            ("PAR_BB", "count1", "count1"),
        ),
        compile("count0 = 13\ncount1 = const0", "<string>", "exec"),
        (
            ("PAR_CONST", 14, "const0"),
        ),
    ),
    (),
    "compute0"
)

wait0 = (
    "NT_WAIT",
    "goon",
    (),
    "wait0",
)

seq = (
    "NT_SEQ",
    (),
    (always0, always1, compute0, wait0),
    "seq",
)

root = (
    "NT_ROOT",
    (),
    (seq,),
    "root",
)
