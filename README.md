# pystatus

This is an i3bar compatible, modular status line generator. You can use
this for your i3 desktop to generate a status line according to your wish.

If there are modules missing for your need, you can simply create your own one.

## Configuration

A full example can be found in the distributed *pystatus.cfg* file. The file
has to be placed under *${HOME}/.config/pystatus/pystatus.cfg*.

Alternatively your may specify your own path by passing *-c PATH* to pystatus.

Simple example to only display current wifi status and wall clock:
```xml
<?xml version="1.0"?>
<pystatus>
    <blocks>
        <block plugin="wifi" name="wlan0"/>
        <block plugin="clock"/>
    </blocks>
</pystatus>
```

## Use in i3

pystatus is fully compatible to the i3bar protocol and thus can be used as
drop in replacement for i3status.

A simple configuration within your i3 config may look like

```
bar {
    i3bar_command i3bar
    status_command pystatus
    position bottom
}
```

## Logging

pystatus also supports simple logging. This helps you identify problems with
your setup or with pystatus itself.

By default pystatus will log to stderr. You can configure the logging by
creating *~/.config/pystatus/logging.cfg*. Alternatively you may pass
*--log-config PATH* to pystatus.

You may copy the distributed *logging.cfg* which will configure logging to
*/tmp/pystatus.log*.

More informations on how to configure logging can be read
[here](https://docs.python.org/3.6/library/logging.config.html#logging-config-fileformat).

## Custom modules

Documentation incoming.
