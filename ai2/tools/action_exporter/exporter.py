import importlib
import inspect
import json

from ai2.runtime.mode import set_export

class Exporter(object):
    def __init__(self):
        set_export()
        self.targets = set()
        self.root = None

    def add_target(self, *args):
        for a in args:
            self.targets.add(a)

    def export(self, path="actions.json"):
        export_dict = {}
        for module in self.targets:
            m = importlib.import_module(module, self.root)
            for c in m.__exported__:
                current_class = []
                export_dict[c.__name__] = current_class
                for action in c.__exported__:
                    arg_spec = inspect.getargspec(action)
                    args = arg_spec.args
                    if len(args) < 2:
                        print("action function should have at least 2 arguments: self, node")
                        assert(False)
                    current_action_args = arg_spec.args[2:]
                    current_class.append([action.__name__] + current_action_args)

        with open(path, "wb") as ofile:
            json.dump(export_dict, ofile, indent=4)


def run():
    e = Exporter()
    e.add_target(
        "ai2.runtime.agent"
    )
    e.export()
