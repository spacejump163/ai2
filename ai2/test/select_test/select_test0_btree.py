
info = __file__


NT_ACT8 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS4 = ('NT_ALWAYS', False, (NT_ACT8,), '')


NT_ACT9 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS5 = ('NT_ALWAYS', False, (NT_ACT9,), '')


NT_COMP6 = ('NT_COMP',
 (compile('count0 = 13\ncount1 = const0', "<string>", "exec"),
  [('PAR_CONST', 14, 'const0')],
  [['PAR_BB', 'count0', 'count0'],
   ['PAR_BB', 'count1', 'count1']]),
 (),
 '')


NT_WAIT7 = ('NT_WAIT', 'goon', (), '')


NT_SEL2 = ('NT_SEL',
 (),
 (NT_ALWAYS4,
  NT_ALWAYS5,
  NT_COMP6,
  NT_WAIT7),
 '')


NT_WAIT3 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ', (), (NT_SEL2, NT_WAIT3), '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
