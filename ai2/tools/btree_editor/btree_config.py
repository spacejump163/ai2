import sys
import os
PATH = "./btree_config.json"
from ai2.tools.config import ConfigModule

class BTreeConfig(ConfigModule):
    def init_dict(self):
        cdir = os.path.abspath(os.getcwd())
        d = {
            "export_path": os.path.join(cdir, "export"),
            "src_path": os.path.join(cdir, "btree"),
        }
        return d


config = BTreeConfig(PATH)

UNIT = 10