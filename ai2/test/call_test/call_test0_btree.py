
info = __file__


NT_COMP2 = ('NT_COMP',
 (compile('\nc0 = 0\nc1 = 0', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt0', 'c0'],
   ['PAR_BB', 'cnt1', 'c1']]),
 (),
 '')


NT_CALL3 = ('NT_CALL',
 'call_test.call_test1_btree',
 (),
 '')


NT_CALL4 = ('NT_CALL',
 'call_test.call_test2_btree',
 (),
 '')


NT_CALL7 = ('NT_CALL',
 'call_test.call_test1_btree',
 (),
 '')


NT_CALL8 = ('NT_CALL',
 'call_test.call_test2_btree',
 (),
 '')


NT_WAIT9 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_COMP2,
  NT_CALL3,
  NT_CALL4,
  NT_CALL7,
  NT_CALL8,
  NT_WAIT9),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
