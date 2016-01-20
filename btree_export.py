
info = __file__


NT_ACT3 = ('NT_ACT',
 (('aaaaaaaaaaaaaaaaa0',), ('',)),
 (),
 '')


NT_SEQ2 = ('NT_SEQ', (), (NT_ACT3,), '')


NT_COMP5 = ('NT_COMP',
 ((),
  compile('', "<string>", "exec"),
  ()),
 (),
 '')


NT_COMP6 = ('NT_COMP',
 ((),
  compile('', "<string>", "exec"),
  ()),
 (),
 '')


NT_COMP7 = ('NT_COMP',
 ((),
  compile('', "<string>", "exec"),
  ()),
 (),
 '')


NT_SEQ4 = ('NT_SEQ',
 (),
 (NT_COMP5, NT_COMP6, NT_COMP7),
 '')


NT_ACT9 = ('NT_ACT', (('aa4',), ('',)), (), '')


NT_ACT10 = ('NT_ACT', (('aaa5',), ('',)), (), '')


NT_SEQ8 = ('NT_SEQ', (), (NT_ACT9, NT_ACT10), '')


NT_ACT11 = ('NT_ACT',
 (('aaaaaaaaaaaaa6',), ('',)),
 (),
 '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_SEQ2, NT_SEQ4, NT_SEQ8, NT_ACT11),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
