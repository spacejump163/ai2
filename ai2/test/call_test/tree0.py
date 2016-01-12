info = __file__


comp_init = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt0", "c0"),
            ("PAR_BB", "cnt1", "c1"),
        ),
        compile("c0 = 0; c1 = 0", "<string>", "exec"),
        (),
    ),
    (),
    "init"
)

call_sub0 = (
    "NT_CALL",
    "call_test.subtree0",
    (),
    "call subtree 0"
)

call_sub1 = (
    "NT_CALL",
    "call_test.subtree1",
    (),
    "call subtree 1"
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
    (comp_init, call_sub0, call_sub1, call_sub0, call_sub1, wait0),
    "seq"
)

root = (
    "NT_ROOT",
    (),
    (seq,),
    "root",
)
