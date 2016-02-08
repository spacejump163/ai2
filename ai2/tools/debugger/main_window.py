# -*- encoding: utf-8 -*-
import logging
import sys
import os

from PyQt5.QtWidgets import \
    QApplication, QTabWidget, QMdiArea, QDialog, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
import functools

from ai2.tools.debugger.instance_vm import GraphInstanceVM
from ai2.tools.console_debugger.debugger import DebugClient

this_path = os.path.dirname(__file__)
MAIN_UI_PATH = os.path.join(this_path, "../../../res/gui/debugger_main.ui")
WELCOME_UI_PATH = os.path.join(this_path, "../../../res/gui/debugger_welcome.ui")
SELECT_AGENT_UI_PATH = os.path.join(this_path, "../../../res/gui/debugger_select_agent.ui")

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class DebuggerMainWindow(object):
    def __init__(self, comm):
        self.comm = comm
        self.follow_state = True
        self.init_instances()
        self.init_widgets()
        self.init_actions()
        self.window.closeEvent = self.close_handler
        self.window.showMaximized()

    def run(self):
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_handler)
        self.comm.start_worker()
        self.poll_timer.start(1000)

    def poll_handler(self):
        self.comm.put_job(self.comm.get_agent_track)
        data = self.comm.take_data()
        for location_info, state in data:
            file_name, node_id = location_info
            i = self.get_instance(file_name)

            if i is None:
                text = "%s:%s" % (str(location_info), state)
            else:
                node = i.model.get_node(node_id)
                if node is not None:
                    text = "%s: %s: %s" % (file_name, node.get_display_text(), state)
                else:
                    text = "%s:%s" % (str(location_info), state)
            self.add_to_history_list(location_info, text)
        if self.follow_state:
            self.focus_last()

    def init_widgets(self):
        self.window = loadUi(MAIN_UI_PATH)
        self.mdi = self.window.mdiArea
        self.mdi.setViewMode(QMdiArea.TabbedView)
        self.mdi.setTabsMovable(True)
        self.mdi.setTabsClosable(True)
        self.mdi.setTabShape(QTabWidget.Rounded)
        self.dock_anchor = self.window.dockAnchor
        self.dock_anchor.layout().setAlignment(Qt.AlignTop)

        self.history_list = QListWidget()
        self.history_list.itemSelectionChanged.connect(self.list_item_selected)
        self.add_dock_content(self.history_list)

    def list_item_selected(self):
        citem = self.history_list.currentItem()
        self.focus_on_location(citem.location_info)

    def init_instances(self):
        self.instances = {}

    def remove_instance(self, ins):
        file_name = ins.file_name
        self.instances.pop(file_name)

    def add_instance(self, ins):
        file_name = ins.file_name
        self.instances[file_name] = ins

    def get_instance(self, file_name):
        if file_name in self.instances:
            return self.instances[file_name]
        else:
            full_path = GraphInstanceVM.get_full_path(file_name)
            model = GraphInstanceVM.get_model(full_path)
            if model is None:
                return None
            ins = GraphInstanceVM(model, self, file_name)
            return ins

    def init_actions(self):
        self.window.actionResume.triggered.connect(self.action_resume_handler)
        self.window.actionStop.triggered.connect(self.action_stop_handler)
        self.window.actionFollow.triggered.connect(self.action_follow_handler)
        self.window.actionHold.triggered.connect(self.action_hold_handler)

    def action_resume_handler(self):
        self.clear_list()
        self.comm.put_job(functools.partial(self.comm.track_agent, True))

    def action_stop_handler(self):
        self.comm.put_job(functools.partial(self.comm.track_agent, False))

    def action_follow_handler(self):
        self.follow_state = True

    def action_hold_handler(self):
        self.follow_state = False

    def close_handler(self, ev):
        # disable tracking for some agents
        self.poll_timer.stop()
        self.comm.put_job(self.comm.finish)
        self.comm.shutdown()

    def add_dock_content(self, widget):
        self.clear_dock_contents()
        self.dock_anchor.layout().addWidget(widget)

    def get_dock_contents(self):
        l = self.dock_anchor.layout()
        ret = []
        for i in range(l.count()):
            ret.append(l.itemAt(i).widget())
        return ret

    def clear_dock_contents(self):
        ws = self.get_dock_contents()
        for w in ws:
            w.deleteLater()

    def focus_on_location(self, location):
        file_name, node_id = location
        instance = self.get_instance(file_name)
        if instance is None:
            logger.fatal("can not find src file for %s" % file_name)
            return False
        ret = instance.focus_on(node_id)
        if ret is False:
            logger.fatal("can not find node %s for %s" % (node_id, file_name))
            return False
        return True

    def add_to_history_list(self, location, text):
        item = HistoryListItem(location, text)
        self.history_list.addItem(item)

    def clear_list(self):
        self.history_list.clear()

    def focus_last(self):
        c = self.history_list.count()
        if c > 0:
            item = self.history_list.item(c-1)
            self.history_list.setCurrentItem(item)
            self.focus_on_location(item.location_info)


class HistoryListItem(QListWidgetItem):
    def __init__(self, location_info, text):
        self.location_info = location_info
        super(HistoryListItem, self).__init__(text)


def setup_comm():
    welcome_dialog = loadUi(WELCOME_UI_PATH)
    welcome_dialog.exec()
    ip = welcome_dialog.ip_edit.toPlainText()
    port = welcome_dialog.port_edit.toPlainText()

    comm = DebugClient(ip, port)
    comm.connect()
    ret = comm.get_agent_list()
    if len(ret) == 0:
        return None
    agent_list = ret
    select_agent_dialog = loadUi(SELECT_AGENT_UI_PATH)
    for i in agent_list:
        select_agent_dialog.listWidget.addItem(i)
    ret = select_agent_dialog.exec()
    if ret == QDialog.Rejected:
        return None
    idx = select_agent_dialog.listWidget.currentRow()
    comm.set_agent_id(agent_list[idx])
    comm.track_agent(True)
    return comm


def run():
    app = QApplication(sys.argv)
    comm = setup_comm()
    #comm = None
    window = DebuggerMainWindow(comm)
    window.run()
    app.exec_()


