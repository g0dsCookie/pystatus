from pystatus.internal import (
    clock, cpu,
    disk,
    loadavg,
    memory,
    temperature,
    uptime,
    zfs
)

PLUGINS = [
    clock.Clock, cpu.CPU,
    disk.Disk,
    loadavg.Loadavg,
    memory.Memory,
    temperature.Temperature,
    uptime.Uptime,
    zfs.ZFS,
]
