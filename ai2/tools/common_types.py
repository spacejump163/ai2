import ai2.runtime.defs as defs

class ParamItem(object):
    CATEGORIES = (defs.PAR_CONST, defs.PAR_BB, defs.PAR_PROP)
    def __init__(self, category, name):
        self.category = category
        self.name = name

    def set_category_by_index(self, idx):
        self.category = self.CATEGORIES[idx]

    def get_category_index(self):
        return self.CATEGORIES.index(self.category)

    def to_tuple(self):
        return self.category, self.name