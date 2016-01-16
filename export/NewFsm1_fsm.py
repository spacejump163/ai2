
info = __file__

states = \
(('start',
  (('log',
    ('PAR_CONST', 'in start state')),
   ('log',
    ('PAR_CONST',
     'we can log more'))),
  (('log',
    ('PAR_CONST',
     'leaving start state')),)),
 ('end',
  (('log',
    ('PAR_CONST',
     'enter end state')),),
  (('log',
    ('PAR_CONST',
     'leaving end state')),)))

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

