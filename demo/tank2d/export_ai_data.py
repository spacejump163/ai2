# -*- encoding: utf-8 -*-
from ai2.tools.action_exporter.exporter import Exporter

if __name__ == "__main__":
    e = Exporter()
    e.add_target(
        "ai2.runtime.action_agent",
        "tank_agent"
    )
    e.export("ai_prj/actions.json")