
info = __file__


NT_COMP7 = ('NT_COMP',
 (compile('cnt = 4', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_ALWAYS4 = ('NT_ALWAYS', False, (NT_COMP7,), '')


NT_COMP5 = ('NT_COMP',
 (compile('cnt = 0\n', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_WAIT6 = ('NT_WAIT', 'goon', (), '')


NT_SEQ2 = ('NT_SEQ',
 (),
 (NT_ALWAYS4, NT_COMP5, NT_WAIT6),
 '')


NT_WAIT3 = ('NT_WAIT', 'goon', (), '')


NT_SEL1 = ('NT_SEL', (), (NT_SEQ2, NT_WAIT3), '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEL1,), '')


root = NT_ROOT0
