
info = __file__


NT_COMP2 = ('NT_COMP',
 (compile('c0 += 1', "<string>", 'exec'),
  [['PAR_BB', 'cnt1', 'c0']],
  [['PAR_BB', 'cnt1', 'c0']]),
 (),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_COMP2,), '')


root = NT_ROOT0
