from pystatus.internal import (clock, cpu, loadavg, memory, uptime, zfs)

PLUGINS = [
    clock.Clock,
    cpu.CPU,
    loadavg.Loadavg,
    memory.Memory,
    uptime.Uptime,
    zfs.ZFS,
]
