info = __file__


inc = (
    "NT_COMP",
    (
        (
            ("PAR_BB", "cnt1", "c0"),
        ),
        compile("c0 += 1", "<string>", "exec"),
        (
            ("PAR_BB", "cnt1", "c0"),
        ),
    ),
    (),
    "inc cnt1"
)

root = (
    "NT_ROOT",
    (),
    (inc,),
    "root",
)
