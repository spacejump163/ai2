
info = __file__


NT_CALL3 = ('NT_CALL',
 'call_test.call_test2_btree',
 (),
 '')


NT_COMP4 = ('NT_COMP',
 (compile('c0 += 1', "<string>", 'exec'),
  [['PAR_BB', 'cnt0', 'c0']],
  [['PAR_BB', 'cnt0', 'c0']]),
 (),
 '')


NT_SEQ2 = ('NT_SEQ',
 (),
 (NT_CALL3, NT_COMP4),
 '')


NT_ALWAYS1 = ('NT_ALWAYS', True, (NT_SEQ2,), '')


NT_ROOT0 = ('NT_ROOT', (), (NT_ALWAYS1,), '')


root = NT_ROOT0
