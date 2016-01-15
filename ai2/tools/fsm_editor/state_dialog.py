# -*- encoding: utf-8 -*-
import sys
import os

import functools

from PyQt5.uic import loadUi


import ai2.tools.fsm_editor.common_dialog as cdialog
from ai2.tools.fsm_editor.model import ActionItem
from ai2.tools.param_dialog import ParamDialog

this_path = os.path.dirname(__file__)
STATE_DETAIL_DIALOG_PATH = os.path.join(this_path, "../../../res/gui/fsm_state_detail_dialog.ui")
LIST_EDIT_PANEL_PATH = os.path.join(this_path, "../../../res/gui/list_edit.ui")


class ActionListModel(cdialog.SimpleListModel):
    def value_to_display(self, value):
        frags = []
        frags.append(value.name + ":")
        for a in value.args:
            frags.append("(%s:%s);" % (a.category, a.name))
        return "".join(frags)


class ParamListModel(cdialog.SimpleListModel):
    def value_to_display(self, value):
        s = "%s:%s" % (value.category, value.name)
        return s


class StateDetailDialogVM(object):
    def __init__(self, state_item):
        super(StateDetailDialogVM, self).__init__()
        self.state_item = state_item
        self.selected_action = ActionItem()
        self.init_ui()
        self.init_vms()

    def init_ui(self):
        w  = loadUi(STATE_DETAIL_DIALOG_PATH)
        self.window = w
        self.edit_panels = []
        for lay in (w.layout0, w.layout1, w.layout2):
            edit_panel = loadUi(LIST_EDIT_PANEL_PATH)
            lay.addWidget(edit_panel)
            self.edit_panels.append(edit_panel)
        for i in range(0, 2):
            self.edit_panels[i].view.currentChanged = functools.partial(self.selection_changed_handler, i)

    def init_action_list_vm(self, category, window):
        action_list = getattr(self.state_item, category)
        container_vm = ActionListModel(action_list)
        add_item = functools.partial(self.state_item.add_item, category)
        remove_item = functools.partial(self.state_item.remove_item, category)
        action_list_vm = StateActionListPanelVM(
            container_vm,
            action_list,
            add_item,
            remove_item,
            window)
        self.vms.append(action_list_vm)

    def build_action_detail_param_vm(self):
        selected = self.selected_action
        model_list = self.selected_action.args
        container_vm = ParamListModel(model_list)
        add_item = selected.add_item
        remove_item = selected.remove_item
        return container_vm, model_list, add_item, remove_item

    def init_action_detail_param_vm(self):
        container_vm, model_list, add_item, remove_item = \
            self.build_action_detail_param_vm()
        action_detail_vm = StateActionDetailParamPanelVM(
            container_vm,
            model_list,
            add_item,
            remove_item,
            self.edit_panels[2])
        action_detail_vm.set_parent_vm(self)
        self.vms.append(action_detail_vm)

    def init_action_detail_misc_vm(self):
        selected = self.selected_action
        misc_vm = StateActionDetailMiscPanelVM(self.window, selected)
        misc_vm.set_parent_vm(self)
        self.vms.append(misc_vm)

    def init_vms(self):
        self.vms = []
        self.init_action_list_vm("enter_actions", self.edit_panels[0])
        self.init_action_list_vm("leave_actions", self.edit_panels[1])
        self.init_action_detail_misc_vm()
        self.init_action_detail_param_vm()


    def run(self):
        #self.window.show()
        self.window.exec()
        pass

    def selection_changed_handler(self, widget_idx, idx, idx_old):
        item_list = None
        if widget_idx == 0:
            item_list = self.state_item.enter_actions
        elif widget_idx == 1:
            item_list = self.state_item.leave_actions
        else:
            assert(False)
        row = idx.row()
        self.selected_action = item_list[row]
        #notify 2 vm looking depending on this
        self.vms[2].change_model(self.selected_action)
        margs = self.build_action_detail_param_vm()
        self.vms[3].change_model(*margs)

    def refresh(self):
        # this is embarassing
        for vm in self.vms[0:2]:
            vm.refresh()


class StateListPanelVM(cdialog.ListEditPanelVM):
    def __init__(self, container_vm, container_model, item_ctor, item_dtor, window):
        super(StateListPanelVM, self).__init__(
            container_vm, container_model, item_ctor, item_dtor, window)
        #self.window.view.doubleClicked = self.edit_handler

    def edit_handler(self):
        i = self.get_selection_index()
        state_item = self.model_list[i]
        dialog = StateDetailDialogVM(state_item)
        dialog.run()


class StateActionListPanelVM(cdialog.ListEditPanelVM):
    def __init__(self, container_vm, container_model, item_ctor, item_dtor, window):
        super(StateActionListPanelVM, self).__init__(
            container_vm, container_model, item_ctor, item_dtor, window)


class StateActionDetailParamPanelVM(cdialog.ListEditPanelVM):
    def __init__(self, *args, **kwargs):
        super(StateActionDetailParamPanelVM, self).__init__(*args, **kwargs)

    def set_parent_vm(self, vm):
        self.parent_vm = vm

    def edit_handler(self):
        i = self.get_selection_index()
        param_item = self.model_list[i]
        dialog = ParamDialog(param_item)
        dialog.run()
        self.parent_vm.refresh()

    def refresh(self):
        super(StateActionDetailParamPanelVM, self).refresh()
        self.parent_vm.refresh()


class StateActionDetailMiscPanelVM(object):
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.changed = None
        self.window.name_edit.textEdited.connect(self.update_model)

    def set_parent_vm(self, vm):
        self.parent_vm = vm

    def change_model(self, model):
        self.model = model
        self.window.name_edit.setText(model.name)

    def update_model(self, text):
        self.model.name = text
        self.parent_vm.refresh()


def test():
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    from ai2.tools.fsm_editor.model import StateItem
    import ai2.runtime.defs as defs
    state_item = StateItem("test_state", 123)
    act1 = state_item.add_item("enter_actions")
    act1.name = "log"
    p = act1.add_item()
    p.category = defs.PAR_BB
    p.name = "hello"
    act2 = state_item.add_item("enter_actions")
    act2.name = "tree"
    p = act2.add_item()
    p.category = defs.PAR_CONST
    p.name = "consts.py"

    app = QApplication(sys.argv)

    dialog = StateDetailDialogVM(state_item)
    dialog.run()


