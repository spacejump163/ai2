# -*- encoding: utf-8 -*-

COMPLETE = "complete"
EXPORT = "export"

mode = COMPLETE

def set_complete():
    global mode
    mode = COMPLETE

def set_export():
    global mode
    mode = EXPORT

def is_complete():
    return mode == COMPLETE
