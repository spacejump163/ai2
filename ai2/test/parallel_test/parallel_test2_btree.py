
info = __file__


NT_ACT4 = ('NT_ACT',
 (['test_action_enter',
   ('PAR_CONST', 22)],
  ['test_action_leave',
   ('PAR_CONST', 22)]),
 (),
 '')


NT_ACT5 = ('NT_ACT',
 (['test_action_enter',
   ('PAR_CONST', 33)],
  ['test_action_leave',
   ('PAR_CONST', 33)]),
 (),
 '')


NT_WAIT6 = ('NT_WAIT', 'timeout', (), '')


NT_PARL2 = ('NT_PARL',
 (),
 (NT_ACT4, NT_ACT5, NT_WAIT6),
 '')


NT_WAIT3 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_PARL2, NT_WAIT3),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
