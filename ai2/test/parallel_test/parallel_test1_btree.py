
info = __file__


NT_ACT9 = ('NT_ACT',
 (['test_action_enter',
   ('PAR_CONST', 22)],
  ['test_action_leave',
   ('PAR_CONST', 22)]),
 (),
 '')


NT_ACT10 = ('NT_ACT',
 (['test_action_enter',
   ('PAR_CONST', 33)],
  ['test_action_leave',
   ('PAR_CONST', 33)]),
 (),
 '')


NT_WAIT11 = ('NT_WAIT', 'timeout', (), '')


NT_PARL8 = ('NT_PARL',
 (),
 (NT_ACT9, NT_ACT10, NT_WAIT11),
 '')


NT_WAIT12 = ('NT_WAIT', 'goon', (), '')


NT_SEL7 = ('NT_SEL',
 (),
 (NT_PARL8, NT_WAIT12),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEL7,), '')


root = NT_ROOT0
