from pystatus.internal import (
    battery,
    clock, cpu,
    disk,
    loadavg,
    memory,
    temperature,
    uptime,
    wifi,
    zfs,
)

PLUGINS = [
    battery.Battery,
    clock.Clock, cpu.CPU,
    disk.Disk,
    loadavg.Loadavg,
    memory.Memory,
    temperature.Temperature,
    uptime.Uptime,
    wifi.WifiPlugin,
    zfs.ZFS,
]
