# -*- encoding: utf-8 -*-
import os
import sys
import time
import threading
import queue
import logging
import collections
from xmlrpc.client import ServerProxy

logger = logging.getLogger("debugger")


class DebugClient(object):
    def __init__(self, addr, port):
        self.server = None
        self.addr_str = "http://%s:%s/" % (addr, port)
        self.agent_id = None
        self.worker = None
        self.data = []
        self.jobs = queue.Queue(16)
        self.lock = threading.Lock()

    def is_valid(self):
        return self.server is not None

    def connect(self):
        self.server = None
        self.server = ServerProxy(self.addr_str)
        try:
            ret = self.server.handshake()
            return True, ret
        except Exception as e:
            return False, e

    def get_agent_list(self):
        return self.server.get_agent_list()

    def set_agent_id(self, id):
        self.agent_id = id

    def track_agent(self, on_off):
        return self.server.track_agent(self.agent_id, on_off)

    def get_agent_track(self):
        ret = self.server.get_agent_track(self.agent_id)
        if ret is False:
            return False
        self.lock.acquire()
        self.data += ret
        self.lock.release()

    def finish(self):
        try:
            self.track_agent(False)
        except:
            pass
        return True

    def start_worker(self):
        assert(self.worker is None)
        self.worker = threading.Thread(target=self.worker_body)
        self.worker.start()

    def put_job(self, work, priority = 100):
        self.jobs.put((priority, work))

    def worker_body(self):
        while True:
            if self.server is None:
                try:
                    self.connect()
                except:
                    pass
                continue

            _, job = self.jobs.get(True)
            try:
                ret = job()
            except:
                ret = False
            if job == self.finish:
                return
            if ret is False:
                logger.fatal("error connection reset")
                self.server = None

    ###########################################################################
    # outer API
    ###########################################################################
    def shutdown(self):
        self.jobs.put(self.finish)
        self.worker.join()

    def take_data(self):
        self.lock.acquire()
        ret, self.data = self.data, []
        self.lock.release()
        return ret


def run():
    client = DebugClient("localhost", 8000)
    ret = client.connect()
    ret = client.get_agent_list()
    agent_id = None
    if len(ret) > 0:
        agent_id = ret[0]
        client.set_agent_id(agent_id)
        client.track_agent(True)
    while True:
        ret = client.get_agent_track()
        if ret is False:
            break
        for i in ret:
            print(i)

