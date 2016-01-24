
info = __file__


NT_COMP2 = ('NT_COMP',
 ('cnt = 0',
  [],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_COMP5 = ('NT_COMP',
 ('cnt == 4',
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_COMP6 = ('NT_COMP',
 ('cnt += 1',
  [['PAR_BB', 'cnt', 'cnt']],
  [['PAR_BB', 'cnt', 'cnt']]),
 (),
 '')


NT_UNTIL3 = ('NT_UNTIL',
 (),
 (NT_COMP5, NT_COMP6),
 '')


NT_WAIT4 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_COMP2, NT_UNTIL3, NT_WAIT4),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
