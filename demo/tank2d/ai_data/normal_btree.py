
# -*- encoding: utf-8 -*-
__src_file__ = 'normal.btree'

NT_ACT4 = ('NT_ACT',
 (['move_to_point_start',
   ('PAR_CONST', (0, 0)),
   ('PAR_CONST', 1.0),
   ('PAR_CONST', 1)],
  ['move_to_common_end']),
 (),
 (__src_file__, 4))


NT_ACT9 = ('NT_ACT',
 (['log_position'], ['']),
 (),
 (__src_file__, 9))


NT_ACT10 = ('NT_ACT',
 (['move_to_point_start',
   ('PAR_CONST', (5, 0)),
   ('PAR_CONST', 1.0),
   ('PAR_CONST', 1)],
  ['move_to_common_end']),
 (),
 (__src_file__, 10))


NT_ACT11 = ('NT_ACT',
 (['log_position'], ['']),
 (),
 (__src_file__, 11))


NT_ACT12 = ('NT_ACT',
 (['move_to_point_start',
   ('PAR_CONST', (0, 5)),
   ('PAR_CONST', 1.0),
   ('PAR_CONST', 1)],
  ['move_to_common_end']),
 (),
 (__src_file__, 12))


NT_ACT13 = ('NT_ACT',
 (['log_position'], ['']),
 (),
 (__src_file__, 13))


NT_ACT15 = ('NT_ACT',
 (['select_target'], ['']),
 (),
 (__src_file__, 15))


NT_ACT16 = ('NT_ACT',
 (['target_valid'], ['']),
 (),
 (__src_file__, 16))


NT_ACT17 = ('NT_ACT',
 (['start_aiming_at_target'], ['']),
 (),
 (__src_file__, 17))


NT_ACT18 = ('NT_ACT',
 (['start_firing'], ['']),
 (),
 (__src_file__, 18))


NT_SEQ14 = ('NT_SEQ',
 (),
 (NT_ACT15,
  NT_ACT16,
  NT_ACT17,
  NT_ACT18),
 (__src_file__, 14))


NT_SEQ1 = ('NT_SEQ',
 (),
 (NT_ACT4,
  NT_ACT9,
  NT_ACT10,
  NT_ACT11,
  NT_ACT12,
  NT_ACT13,
  NT_SEQ14),
 (__src_file__, 1))


NT_ROOT0 = ('NT_ROOT',
 (),
 (NT_SEQ1,),
 (__src_file__, 0))


root = NT_ROOT0
