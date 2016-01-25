
info = __file__


NT_COMP2 = ('NT_COMP',
 (compile('cnt = 0', "<string>", 'exec'),
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_COND5 = ('NT_COND',
 (compile('cnt == 4', "<string>", 'eval'),
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_COMP6 = ('NT_COMP',
 (compile('cnt += 1', "<string>", 'exec'),
  [['PAR_BB', 'cnt', 'cnt']],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_UNTIL3 = ('NT_UNTIL',
 (),
 (NT_COND5, NT_COMP6),
 '')


NT_WAIT4 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_COMP2, NT_UNTIL3, NT_WAIT4),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
