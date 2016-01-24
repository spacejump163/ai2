
info = __file__


NT_COMP2 = ('NT_COMP',
 (compile('ret = ""', "<string>", "exec"),
  [],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP8 = ('NT_COMP',
 (compile('ret = "1" + ret', "<string>", "exec"),
  [['PAR_BB', 'ret', 'ret']],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP11 = ('NT_COMP',
 (compile('ret = "2" + ret', "<string>", "exec"),
  [['PAR_BB', 'ret', 'ret']],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_COMP12 = ('NT_COMP',
 (compile('ret = "3" + ret', "<string>", "exec"),
  [['PAR_BB', 'ret', 'ret']],
  [['PAR_BB', 'ret', 'ret']]),
 (),
 '')


NT_RSEQ3 = ('NT_RSEQ',
 (),
 (NT_COMP8, NT_COMP11, NT_COMP12),
 '')


NT_WAIT4 = ('NT_WAIT', 'goon', (), '')


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_COMP2, NT_RSEQ3, NT_WAIT4),
 '')


NT_ROOT0 = ('NT_ROOT', (), (NT_SEQ1,), '')


root = NT_ROOT0
