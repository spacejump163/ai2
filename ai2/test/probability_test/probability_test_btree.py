
info = __file__


NT_COMP4 = ('NT_COMP',
 (compile('ret = 0', "<string>", "exec"),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP5 = ('NT_COMP',
 (compile('ret = 1', "<string>", "exec"),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP6 = ('NT_COMP',
 (compile('ret = 2', "<string>", "exec"),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_PSEL2 = ('NT_PSEL',
 (1.0, 4.0, 10.0),
 (NT_COMP4, NT_COMP5, NT_COMP6),
 '')


NT_WAIT3 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_PSEL2, NT_WAIT3),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
