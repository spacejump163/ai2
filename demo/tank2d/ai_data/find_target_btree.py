
# -*- encoding: utf-8 -*-
__src_file__ = 'find_target.btree'

NT_ACT17 = ('NT_ACT',
 (['target_valid'], ['']),
 (),
 (__src_file__, 17))


NT_ACT19 = ('NT_ACT',
 (['select_target'], ['']),
 (),
 (__src_file__, 19))


NT_ACT32 = ('NT_ACT',
 (['log', ('PAR_CONST', '开始闲逛')],
  ['']),
 (),
 (__src_file__, 32))


NT_ACT33 = ('NT_ACT',
 (['wait_for_n_sec',
   ('PAR_CONST', 2.0)],
  ['wait_for_n_sec_stop']),
 (),
 (__src_file__, 33))


NT_SEQ31 = ('NT_SEQ',
 (),
 (NT_ACT32, NT_ACT33),
 (__src_file__, 31))


NT_ACT37 = ('NT_ACT',
 (['random_walk_start',
   ('PAR_CONST', 3.0),
   ('PAR_CONST', 4.0)],
  ['move_to_common_end']),
 (),
 (__src_file__, 37))


NT_PARL29 = ('NT_PARL',
 (),
 (NT_SEQ31, NT_ACT37),
 (__src_file__, 29))


NT_COND35 = ('NT_COND',
 (compile('False', "<string>", 'eval'),
  []),
 (),
 (__src_file__, 35))


NT_SEQ28 = ('NT_SEQ',
 (),
 (NT_PARL29, NT_COND35),
 (__src_file__, 28))


NT_SEL18 = ('NT_SEL',
 (),
 (NT_ACT19, NT_SEQ28),
 (__src_file__, 18))


NT_UNTIL16 = ('NT_UNTIL',
 (),
 (NT_ACT17, NT_SEL18),
 (__src_file__, 16))


NT_ROOT0 = ('NT_ROOT',
 (),
 (NT_UNTIL16,),
 (__src_file__, 0))


root = NT_ROOT0
