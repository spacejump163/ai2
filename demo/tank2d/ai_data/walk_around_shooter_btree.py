
# -*- encoding: utf-8 -*-
__src_file__ = 'walk_around_shooter.btree'

NT_CALL16 = ('NT_CALL',
 'find_target_btree',
 (),
 (__src_file__, 16))


NT_ACT52 = ('NT_ACT',
 (['log', ('PAR_CONST', '锁定目标')],
  ['']),
 (),
 (__src_file__, 52))


NT_ACT54 = ('NT_ACT',
 (['aiming_at_target_start'],
  ['aiming_at_target_end']),
 (),
 (__src_file__, 54))


NT_COND56 = ('NT_COND',
 (compile('False', "<string>", 'eval'),
  []),
 (),
 (__src_file__, 56))


NT_ACT58 = ('NT_ACT',
 (['start_firing'], ['']),
 (),
 (__src_file__, 58))


NT_ACT59 = ('NT_ACT',
 (['wait_for_n_sec',
   ('PAR_CONST', 10)],
  ['wait_for_n_sec_stop']),
 (),
 (__src_file__, 59))


NT_ACT60 = ('NT_ACT',
 (['stop_firing'], ['']),
 (),
 (__src_file__, 60))


NT_ACT61 = ('NT_ACT',
 (['wait_for_n_sec',
   ('PAR_CONST', 2)],
  ['wait_for_n_sec_stop']),
 (),
 (__src_file__, 61))


NT_SEQ57 = ('NT_SEQ',
 (),
 (NT_ACT58,
  NT_ACT59,
  NT_ACT60,
  NT_ACT61),
 (__src_file__, 57))


NT_UNTIL55 = ('NT_UNTIL',
 (),
 (NT_COND56, NT_SEQ57),
 (__src_file__, 55))


NT_ACT64 = ('NT_ACT',
 (['target_valid'], ['']),
 (),
 (__src_file__, 64))


NT_NOT63 = ('NT_NOT',
 (),
 (NT_ACT64,),
 (__src_file__, 63))


NT_ACT65 = ('NT_ACT',
 (['wait_for_n_sec',
   ('PAR_CONST', 1.1)],
  ['wait_for_n_sec_stop']),
 (),
 (__src_file__, 65))


NT_UNTIL62 = ('NT_UNTIL',
 (),
 (NT_NOT63, NT_ACT65),
 (__src_file__, 62))


NT_ACT66 = ('NT_ACT',
 (['move_around_target_start',
   ('PAR_CONST', 3),
   ('PAR_CONST', 6),
   ('PAR_CONST', 0.8)],
  ['move_around_target_end']),
 (),
 (__src_file__, 66))


NT_PARL53 = ('NT_PARL',
 (),
 (NT_ACT54,
  NT_UNTIL55,
  NT_UNTIL62,
  NT_ACT66),
 (__src_file__, 53))


NT_SEQ7 = ('NT_SEQ',
 (),
 (NT_CALL16, NT_ACT52, NT_PARL53),
 (__src_file__, 7))


NT_ROOT0 = ('NT_ROOT',
 (),
 (NT_SEQ7,),
 (__src_file__, 0))


root = NT_ROOT0
