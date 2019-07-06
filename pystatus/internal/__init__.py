from pystatus.internal import (
    clock, cpu,
    disk,
    loadavg,
    memory,
    uptime,
    zfs
)

PLUGINS = [
    clock.Clock, cpu.CPU,
    disk.Disk,
    loadavg.Loadavg,
    memory.Memory,
    uptime.Uptime,
    zfs.ZFS,
]
