import importlib
import inspect
import json


class Exporter(object):
    def __init__(self):
        self.targets = set()
        self.root = None

    def add_target(self, *args):
        for a in args:
            self.targets.add(a)

    def export(self, path="actions.json"):
        export_dict = {}
        for package in self.targets:
            m = importlib.import_module(package, self.root)
            current_package = {}
            export_dict[package] = current_package
            for c in m.to_export:
                current_class = {}
                current_package[c.__name__] = current_class
                for action in c.to_export:
                    arg_spec = inspect.getargspec(action)
                    args = arg_spec.args
                    if len(args) < 2:
                        print("action function should have at least 2 arguments: self, node")
                        assert(False)
                    current_action = arg_spec.args[2:]
                    current_class[action.__name__] = current_action

        with open(path, "w", encoding="utf-8") as ofile:
            json.dump(export_dict, ofile, indent=4)


def run():
    e = Exporter()
    e.add_target(
        "ai2.runtime.agent"
    )
    e.export()
