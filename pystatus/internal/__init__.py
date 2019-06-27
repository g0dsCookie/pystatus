from pystatus.internal import (clock, cpu, loadavg, memory, uptime)

PLUGINS = [
    clock.Clock,
    cpu.CPU,
    loadavg.Loadavg,
    memory.Memory,
    uptime.Uptime,
]
