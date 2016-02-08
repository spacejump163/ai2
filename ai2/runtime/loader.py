# -*- encoding: utf-8 -*-
import importlib

import ai2.runtime.defs as defs

_loaded = {}
prefix = ""

def load_fsm(name, force=False):
    return _load_module(name, force, process_loaded_fsm)

def load_btree(name, force=False):
    return _load_module(name, force, process_loaded_btree)

def get_root_desc(name):
    tree = load_btree(name)
    return defs.NodeDesc(*tree.root)

def _load_module(name, force, post_action):
    is_new = True
    full_name = prefix + name
    if full_name in _loaded and not force:
        return _loaded[full_name]
    m = importlib.import_module(full_name)
    processed = post_action(m)
    _loaded[full_name] = processed
    return m

def process_loaded_fsm(fsm_module):
    return fsm_module

def process_loaded_btree(tree_module):
    return tree_module