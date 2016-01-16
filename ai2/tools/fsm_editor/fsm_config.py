import sys
import os
PATH = "./fsm_config.json"
from ai2.tools.config import ConfigModule

class FsmConfig(ConfigModule):
    def init_dict(self):
        cdir = os.path.abspath(os.getcwd())
        d = {
            "export_path": os.path.join(cdir, "export"),
            "src_path": os.path.join(cdir, "fsms"),
        }
        return d


config = FsmConfig(PATH)