import json
import os

DEFAULT_CONFIG_PATH = "./config.json"


class ConfigModule(object):
    KEYS = {"path", "_dict"}
    def __init__(self, path=DEFAULT_CONFIG_PATH):
        self.path = path
        if os.path.exists(path):
            self.load()
        else:
            self._dict = self.init_dict()
            self.dump()

    def init_dict(self):
        return {}

    def __getattr__(self, item):
        return self._dict[item]

    def __setattr__(self, key, value):
        if key in self.KEYS:
            self.__dict__[key] = value
        else:
            self._dict[key] = value

    def dump(self):
        with open(self.path, "w", encoding="utf-8") as outfile:
            json.dump(self._dict, outfile, indent=4)

    def load(self):
        with open(self.path, "r", encoding="utf-8") as infile:
            self._dict = json.load(infile)

    """
    def __del__(self):
        self.dump()
    """


if __name__ == "__main__":
    config = ConfigModule("./config.json")
    config.abc = 1
    config.bbc = "df"
    config.abc = 2
    config.dump()

    config = ConfigModule("./config.json")
    print(config.abc)
    print(config.bbc)