
info = __file__

states = \
(((('log',
    ('PAR_CONST', 'in start state')),
   ('log',
    ('PAR_CONST',
     'we can log more')),
   ('set_blackboard',
    ('PAR_CONST', 'current_state'),
    ('PAR_CONST', '"start"'))),
  (('log',
    ('PAR_CONST',
     'leaving start state')),
   ('set_blackboard',
    ('PAR_CONST', 'current_state'),
    ('PAR_CONST', '""'))),
  'start'),
 ((('log',
    ('PAR_CONST',
     'enter end state')),
   ('set_blackboard',
    ('PAR_CONST', 'current_state'),
    ('PAR_CONST', '"end"'))),
  (('log',
    ('PAR_CONST',
     'leaving end state')),
   ('set_blackboard',
    ('PAR_CONST', 'current_state'),
    ('PAR_CONST', '""'))),
  'end'))

initial_state_index = \
0

events = \
('s', 'e', 't')

graph = \
{(0, 0): 0,
 (0, 1): 1,
 (0, 2): 1,
 (1, 0): 0,
 (1, 1): 1,
 (1, 2): 0}

