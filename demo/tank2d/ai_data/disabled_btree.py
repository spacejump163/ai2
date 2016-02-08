
# -*- encoding: utf-8 -*-
__src_file__ = 'disabled.btree'

NT_COND12 = ('NT_COND',
 (compile('danger_rate > 2', "<string>", 'eval'),
  [['PAR_PROP', 'danger_rate', 'danger_rate']]),
 (),
 (__src_file__, 12))


NT_ACT14 = ('NT_ACT',
 (['escape_start'],
  ['move_to_common_end']),
 (),
 (__src_file__, 14))


NT_SEQ13 = ('NT_SEQ',
 (),
 (NT_ACT14,),
 (__src_file__, 13))


NT_UNTIL11 = ('NT_UNTIL',
 (),
 (NT_COND12, NT_SEQ13),
 (__src_file__, 11))


NT_ACT15 = ('NT_ACT',
 (['trigger_event',
   ('PAR_CONST', 'recover')],
  ['']),
 (),
 (__src_file__, 15))


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_UNTIL11, NT_ACT15),
 (__src_file__, 1))


NT_ROOT0 = ('NT_ROOT',
 (),
 (NT_SEQ1,),
 (__src_file__, 0))


root = NT_ROOT0
