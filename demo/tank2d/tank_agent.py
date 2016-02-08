import functools
import math
import random
import logging

from ai2.runtime.action_agent import \
    ActionAgent, enable_register4export
from ai2.runtime.mode import is_complete

if is_complete():
    from PyQt5.QtCore import QPointF
    import game


class FakeTarget(object):
    def __init__(self, position):
        if isinstance(position, tuple):
            self.position = QPointF(position[0], position[1]) * game.UNIT
        else:
            self.position = position


class NodeState(object):
    pass

enable_register4export()

@register4export
class TankAgent(ActionAgent):
    logger = logging.getLogger("TankAgent")
    enable_register4export()

    def __init__(self, tank):
        super(TankAgent, self).__init__()
        self.tank = tank
        self.attack_target = None

    def start(self, fsm_name):
        self.set_fsm(fsm_name)
        self.enable(True)

    def stop(self):
        self.enable(False)

    @register4export
    def log_position(self, node):
        self.logger.info(
            "%s @(%f, %f)" %
            (self, self.tank.position.x(), self.tank.position.y()))
        node.finish(True)

    @register4export
    def move_to_point_start(self, node, position, speed, limit):
        target = FakeTarget(position)
        self.move_to_common_start(node, target, speed, limit)

    @register4export
    def move_to_target_start(self, node, speed, limit):
        target = self.attack_target
        self.move_to_common_start(node, target, speed, limit)

    @register4export
    def move_to_common_start(self, node, target, speed, limit):
        node.node_state = NodeState()
        node.node_state.aim_body_tick = functools.partial(
            self.tank.aim_body_towards_tick, target, 0)
        self.tank.add_tick(node.node_state.aim_body_tick)

        def check_distance_tick():
            dv = self.tank.position - target.position
            d = dv.manhattanLength()
            if d < limit * game.UNIT:
                node.finish(True)
        node.node_state.timer = self.tank.add_timer(1, check_distance_tick, -1)

        self.tank.move_forward(speed * game.UNIT)

    @register4export
    def move_to_common_end(self, node):
        self.tank.remove_tick(node.node_state.aim_body_tick)
        node.node_state.timer.cancel()
        self.tank.move_speed = 0
        self.tank.rotate_speed = 0

    @register4export
    def move_around_target_start(self, node, near, far, speed_percent):
        ns = node.node_state = NodeState()
        ns.move_tick = functools.partial(
            self.tank.move_around_tick,
            self.attack_target,
            near * game.UNIT, far * game.UNIT, speed_percent)
        self.tank.add_tick(ns.move_tick)

    @register4export
    def move_around_target_end(self, node):
        self.tank.remove_tick(node.node_state.move_tick)

    @register4export
    def start_firing(self, node):
        self.tank.add_tick(self.tank.open_fire)
        node.finish(True)

    @register4export
    def stop_firing(self, node):
        self.tank.remove_tick(self.tank.open_fire)
        node.finish(True)

    @register4export
    def start_aiming_at_target(self, mode):
        aiming_tick = getattr(self, "_aiming_tick", None)
        if aiming_tick:
            self.tank.remove_tick(aiming_tick)
        self._aiming_tick = functools.partial(
            self.tank.estimated_aim_tick,
            self.attack_target)
        self.tank.add_tick(self._aiming_tick)
        node.finish(True)

    def stop_aiming_at_target(self, mode):
        aiming_tick = getattr(self, "_aiming_tick", None)
        if aiming_tick:
            self.tank.remove_tick(aiming_tick)
        self._aiming_tick = None
        node.finish(True)

    @register4export
    def aiming_at_target_start(self, node):
        ns = node.node_state = NodeState()
        ns.tick = functools.partial(
            self.tank.estimated_aim_tick,
            self.attack_target)
        self.tank.add_tick(ns.tick)

    @register4export
    def aiming_at_target_end(self, node):
        ns = node.node_state
        self.tank.remove_tick(ns.tick)

    @register4export
    def target_aimed(self, node):
        a = self.tank.get_shortest_cannon_angle_path_towards(self.attack_target)
        if a < math.pi / 6:
            node.finish(True)
        else:
            node.finish(False)

    @register4export
    def select_target(self, node):
        arena = self.tank.arena
        enemies = arena.get_enemies_in_range(self.tank, 20)
        if enemies:
            self.attack_target = enemies[0]
            node.finish(True)
        else:
            self.attack_target = None
            node.finish(False)

    @register4export
    def target_valid(self, node):
        if self.attack_target and self.attack_target.alive:
            node.finish(True)
            return
        else:
            node.finish(False)
            return

    @register4export
    def wait_for_n_sec(self, node, seconds):
        ns = node.node_state = NodeState()
        def callback():
            #self.logger.info("wait for %f seconds callback" % seconds)
            node.finish(True)
        ns.timer = self.tank.add_timer(seconds, callback, 1)

    @register4export
    def wait_for_n_sec_stop(self, node):
        ns = node.node_state
        ns.timer.cancel()

    @register4export
    def wait_until_danger_exceed_start(self, node, interval, level):
        ns = node.node_state = NodeState()
        def callback():
            if self.danger_rate > level:
                node.finish(True)
        ns.timer = self.tank.add_timer(interval, callback, -1)

    @register4export
    def wait_until_danger_exceed_end(self, node):
        ns = node.node_state
        ns.timer.cancel()

    @register4export
    def random_walk_start(self, node, a, b):
        cpos = self.tank.position
        ra = random.uniform(0, math.pi * 2)
        rd = random.uniform(a, b)
        pos = cpos + QPointF(math.cos(ra) * rd, math.sin(ra) * rd)
        self.move_to_point_start(node, pos, 1.0, 0.5)

    @property
    def my_hp(self):
        return self.tank.hp

    @property
    def target_hp(self):
        return self.attack_target.hp

    @property
    def danger_rate(self):
        return self.get_danger_rate_for_pos(self.tank.position)

    def get_danger_rate_for_pos(self, pos):
        arena = self.tank.arena
        bullets = arena.get_bullets_in_range(self.tank.position, 5 * game.UNIT)
        cpos = self.tank.position
        acc = 0
        for b in bullets:
            bpos = b.position
            dv = cpos - bpos
            dvl = ((dv.x() ** 2) + (dv.y() ** 2)) ** 0.5
            dv = dv * (1.0 / dvl)
            bv = math.cos(b.rotation), math.sin(b.rotation)
            cosa = dv.x() * bv[0] + dv.y() * bv[1]
            acc += self.calc_danger_for_bullet(dvl, cosa)
        return acc

    def calc_danger_for_bullet(self, length, cosa):
        danger_l = game.UNIT * 5 / length
        if danger_l > 5:
            danger_l = 5
        if cosa < 0:
            cosa = 0
        return danger_l * cosa

    @register4export
    def escape_start(self, node):
        cpos = self.tank.position
        candidates = []
        for i in [i * math.pi / 4 for i in range(0, 8)]:
            candidates.append(cpos + QPointF(math.cos(i), math.sin(i)) * 5 * game.UNIT)
        min_danger = 10000
        best = None
        for c in candidates:
            d = self.get_danger_rate_for_pos(c)
            if d < min_danger:
                min_danger = d
                best = c
        self.move_to_point_start(node, best, 1.0, 0.4)

