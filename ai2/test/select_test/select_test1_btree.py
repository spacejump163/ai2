
info = __file__


NT_COMP22 = ('NT_COMP',
 (compile('count0 = 1\ncount1 = 2\n', "<string>", "exec"),
  [],
  [['PAR_BB', 'count0', 'count0'],
   ['PAR_BB', 'count1', 'count1']]),
 (),
 '')


NT_COMP24 = ('NT_COMP',
 (compile('count0 = 3\ncount1 = 4\n', "<string>", "exec"),
  [],
  [['PAR_BB', 'count0', 'count0'],
   ['PAR_BB', 'count1', 'count1']]),
 (),
 '')


NT_ALWAYS23 = ('NT_ALWAYS', True, (NT_COMP24,), '')


NT_WAIT25 = ('NT_WAIT', 'goon', (), '')


NT_SEL21 = ('NT_SEL',
 (),
 (NT_COMP22, NT_ALWAYS23, NT_WAIT25),
 '')


NT_WAIT26 = ('NT_WAIT', 'goon', (), '')


NT_SEQ20 = ('NT_SEQ',
 (),
 (NT_SEL21, NT_WAIT26),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ20,), '')


root = NT_ROOT0
