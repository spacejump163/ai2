import sys
import importlib

if __name__ == "__main__":
    m = importlib.import_module(sys.argv[1])
    m.run()