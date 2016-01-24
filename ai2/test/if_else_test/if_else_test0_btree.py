
info = __file__


NT_COND8 = ('NT_COND',
 (compile('True', "<string>", 'eval'),
  []),
 (),
 '')


NT_COMP9 = ('NT_COMP',
 (compile('ret = 0', "<string>", 'exec'),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP10 = ('NT_COMP',
 (compile('ret = 1', "<string>", 'exec'),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_IF2 = ('NT_IF',
 (),
 (NT_COND8, NT_COMP9, NT_COMP10),
 '')


NT_WAIT3 = ('NT_WAIT', '', (), '')


NT_SEQ1 = ('NT_SEQ', (), (NT_IF2, NT_WAIT3), '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
