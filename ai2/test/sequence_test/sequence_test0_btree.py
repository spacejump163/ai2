
info = __file__


NT_ACT7 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS2 = ('NT_ALWAYS', True, (NT_ACT7,), '')


NT_ACT8 = ('NT_ACT',
 (['nop_enter'], ['']),
 (),
 '')


NT_ALWAYS3 = ('NT_ALWAYS', True, (NT_ACT8,), '')


NT_COMP4 = ('NT_COMP',
 (compile('count0 = 13\ncount1 = const0', "<string>", "exec"),
  [('PAR_CONST', 14, 'const0')],
  [['PAR_BB', 'count0', 'count0'],
   ['PAR_BB', 'count1', 'count1']]),
 (),
 '')


NT_WAIT5 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_ALWAYS2,
  NT_ALWAYS3,
  NT_COMP4,
  NT_WAIT5),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
