
info = __file__

states = \
(((('push_tree',
    ('PAR_BB', 'normal_tree')),),
  (),
  'normal'),
 ((('push_tree',
    ('PAR_BB', 'disabled_tree')),),
  (),
  'disabled'))

initial_state_index = \
0

events = \
('recover', 'damaged')

graph = \
{(0, 1): 1, (1, 0): 0}

