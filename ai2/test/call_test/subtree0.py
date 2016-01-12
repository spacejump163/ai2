info = __file__


inc = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt0", "c0"),
        ),
        compile("c0 += 1", "<string>", "exec"),
        (
            ("PAR_BB", "cnt0", "c0"),
        ),
    ),
    (),
    "inc cnt0"
)

call_subtree1 = (
    "NT_CALL",
    "call_test.subtree1",
    (),
    "call subtree 1"
)

seq = (
    "NT_SEQ",
    (),
    (call_subtree1, inc),
    "seq"
)

always0 = (
    "NT_ALWAYS",
    True,
    (seq,),
    "always true"
)

root = (
    "NT_ROOT",
    (),
    (always0,),
    "root",
)
