
info = __file__


NT_COMP17 = ('NT_COMP',
 (compile('cnt = 1', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_ALWAYS16 = ('NT_ALWAYS', True, (NT_COMP17,), '')


NT_COMP18 = ('NT_COMP',
 (compile('cnt = 2\n', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_WAIT19 = ('NT_WAIT', 'goon', (), '')


NT_SEL9 = ('NT_SEL',
 (),
 (NT_ALWAYS16, NT_COMP18, NT_WAIT19),
 '')


NT_WAIT15 = ('NT_WAIT', 'goon', (), '')


NT_SEQ8 = ('NT_SEQ',
 (),
 (NT_SEL9, NT_WAIT15),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ8,), '')


root = NT_ROOT0
