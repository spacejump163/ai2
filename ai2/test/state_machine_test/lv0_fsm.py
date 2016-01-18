
info = __file__

states = \
(((('set_blackboard',
    ('PAR_CONST', 'state'),
    ('PAR_CONST', '"s00"')),),
  (),
  's00'),
 ((('set_blackboard',
    ('PAR_CONST', 'state'),
    ('PAR_CONST', '"s01"')),
   ('push_fsm',
    ('PAR_CONST',
     'state_machine_test.lv1_fsm'))),
  (),
  's01'),
 ((('set_blackboard',
    ('PAR_CONST', 'state'),
    ('PAR_CONST', '"s02"')),),
  (),
  's02'))

initial_state_index = \
0

events = \
('e1', 'e2', 'e3')

graph = \
{(0, 0): 1, (1, 1): 2, (1, 2): 2}

