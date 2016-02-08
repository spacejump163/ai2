# -*- encoding: utf-8 -*-
import threading
from xmlrpc.server import SimpleXMLRPCServer

class AgentDebugInfo(object):
    STATE_RUNNING = "state_running"
    STATE_BREAKPOINT = "state_blocked"

    def __init__(self, agent, stub):
        self.agent = agent
        self.stub = stub
        self.breakpoints = set()
        self.tracked = False
        self.history = []
        self.stepping = False
        self.state = self.STATE_RUNNING
        self.condition = threading.Condition(stub.lock)

    def wait_for_continue(self):
        self.state = self.STATE_BREAKPOINT
        self.condition.acquire()
        self.condition.wait()

    def check_debug(self, node):
        if not self.tracked:
            return
        self.stub.lock.acquire()
        agent = node.agent
        # collect running history info
        state = node.get_location_info()
        self.history.append(state)
        should_wait = False
        # check breakpoints
        if state in self.breakpoints or self.stepping:
            should_wait = True
        if should_wait:
            self.wait_for_continue()
        else:
            self.stub.lock.release()


class DebugStub(object):
    def __init__(self, port=8000):
        self.lock = threading.Lock()
        self.agents = {}
        self.comm = DebugStubComm(self, port)
        self.worker_thread = threading.Thread(
            name="AIDebugNetWorkerThread",
            target=self.comm.start_service)

    def run(self):
        self.worker_thread.start()

    def stop(self):
        self.comm.server.shutdown()

    def add_agent(self, agent):
        self.lock.acquire()
        self.agents[agent.debug_id] = o = AgentDebugInfo(agent, self)
        agent.debugger = o
        self.lock.release()

    def remove_agent(self, agent):
        self.lock.acquire()
        agent.debugger = None
        del self.agents[agent]
        self.lock.release()


class DebugStubComm(object):

    def __init__(self, stub, port):
        self.stub = stub
        addr = "0.0.0.0"
        self.server = SimpleXMLRPCServer((addr, port))
        self.server.register_function(self.handshake)
        self.server.register_function(self.get_agent_list)
        self.server.register_function(self.track_agent)
        self.server.register_function(self.get_agent_track)


    def start_service(self):
        self.server.serve_forever()

    ###########################################################################
    # client side api
    ###########################################################################
    def get_agent_list(self):
        self.stub.lock.acquire()
        l = [i for i in self.stub.agents]
        self.stub.lock.release()
        return l

    def handshake(self):
        return True

    def track_agent(self, agent_id, on_off):
        self.stub.lock.acquire()
        if agent_id not in self.stub.agents:
            self.stub.lock.release()
            return False
        agent = self.stub.agents[agent_id]
        agent.tracked = on_off
        self.stub.lock.release()
        return True

    def get_agent_track(self, agent_id):
        self.stub.lock.acquire()
        if agent_id not in self.stub.agents:
            self.stub.lock.release()
            return False
        agent = self.stub.agents[agent_id]
        ret = agent.history
        agent.history = []
        self.stub.lock.release()
        return ret

    def set_breakpoint(self, agent_id, location_info):
        pass

    def remove_breakpoint(self, agent_id, location_info):
        pass

    def continue_agent(self, agent_id):
        pass
