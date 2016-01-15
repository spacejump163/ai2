# -*- encoding: utf-8 -*-
import sys
import os

import functools

from PyQt5.uic import loadUi

import ai2.tools.fsm_editor.common_dialog as cdialog
from ai2.tools.fsm_editor.model import ActionItem

this_path = os.path.dirname(__file__)
EDIT_DIALOG_PATH = os.path.join(this_path, "../../res/gui/param_dialog.ui")


class ParamDialog(object):
    def __init__(self, param_item):
        self.param_item = param_item
        self.window = loadUi(EDIT_DIALOG_PATH)
        self.window.type_combo.setCurrentIndex(param_item.get_category_index())
        self.window.type_combo.currentIndexChanged.connect(self.update_type)
        self.window.value_edit.setPlainText(param_item.name)
        self.window.value_edit.textChanged.connect(self.update_text)

    def update_text(self):
        self.param_item.name = self.window.value_edit.toPlainText()

    def update_type(self):
        self.param_item.set_category_by_index(self.window.type_combo.currentIndex())

    def run(self):
        self.window.exec()


def test():
    import sys
    import os
    from PyQt5.QtWidgets import QApplication
    from ai2.tools.fsm_editor.model import ParamItem
    import ai2.runtime.defs as defs
    app = QApplication(sys.argv)
    pmodel = ParamItem(defs.PAR_CONST, "param0")
    dialog = ParamDialog(pmodel)
    dialog.run()
    print(pmodel.to_tuple())