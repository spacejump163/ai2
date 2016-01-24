
info = __file__


NT_COMP4 = ('NT_COMP',
 (compile('count0 = 1\ncount1 = 2', "<string>", "exec"),
  [],
  [['PAR_BB', 'count0', 'count0'],
   ['PAR_BB', 'count1', 'count1']]),
 (),
 '')


NT_ACT8 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS5 = ('NT_ALWAYS', False, (NT_ACT8,), '')


NT_ACT9 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS6 = ('NT_ALWAYS', True, (NT_ACT9,), '')


NT_WAIT7 = ('NT_WAIT', 'goon', (), '')


NT_SEQ2 = ('NT_SEQ',
 (),
 (NT_COMP4,
  NT_ALWAYS5,
  NT_ALWAYS6,
  NT_WAIT7),
 '')


NT_WAIT3 = ('NT_WAIT', 'goon', (), '')


NT_SEL1 = ('NT_SEL', (), (NT_SEQ2, NT_WAIT3), '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEL1,), '')


root = NT_ROOT0
