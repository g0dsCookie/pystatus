import abc
import threading
import time
import importlib.util
import logging
import re
import os
import pystatus.config


class Author:
    def __init__(self, name, email=None):
        self._name = name
        self._email = email

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    def __str__(self):
        if self.email:
            return "%s <%s>" % (self.name, self.email)
        return self.name


class IPlugin(abc.ABC):
    def __init__(self, name, version, author, inst):
        self._name = name
        self._version = version
        self._author = Author(author) if isinstance(author, str) else author
        self._inst = inst
        self._log = logging.getLogger(name)

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def author(self):
        return self._author

    @property
    def log(self):
        return self._log

    def register_option(self, name, fn):
        pystatus.config.Block.register_option(self.name, name, fn)

    def instance(self, name, block, interval, options):
        return self._inst(plugin=self.name, name=name,
                          interval=interval, block=block,
                          **options)


class IInstance(threading.Thread, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self._block = kwargs.get("block")
        if not self._block:
            raise ValueError("block for instance must be defined")
        del kwargs["block"]

        self._stopped = False
        if "interval" in kwargs:
            self._interval = kwargs["interval"]
            del kwargs["interval"]
        else:
            self._interval = 5

        plugin = kwargs.get("plugin")
        if not plugin:
            raise ValueError("plugin for instance must be defined")
        del kwargs["plugin"]
        self._name = kwargs.get("name")
        if not self._name:
            raise ValueError("name for instance must be defined")
        kwargs["name"] = "%s_%s" % (plugin, self._name)
        self._log = logging.getLogger(kwargs["name"])

        # parse plugin options
        options = kwargs.get("options")
        if options:
            for k, v in options.items():
                if k in kwargs:
                    setattr(self, "_%s" % k, kwargs[k])
                    del kwargs[k]
                else:
                    setattr(self, "_%s" % k, v)
            del kwargs["options"]

        return super().__init__(*args, **kwargs)

    @property
    def name(self):
        return self._name

    @property
    def log(self):
        return self._log

    @property
    def block(self):
        return self._block

    @property
    def stopped(self):
        return self._stopped

    @property
    def interval(self):
        return self._interval

    @abc.abstractmethod
    def update(self):
        raise NotImplementedError

    def start(self):
        self._stopped = False
        super().start()

    def stop(self, join=True):
        self._stopped = True
        if join:
            self.join()

    def run(self):
        while not self.stopped:
            self.update()
            time.sleep(self.interval)


class PluginParent:
    def __init__(self):
        self._plugins = {}
        self._instances = {}
        self._log = logging.getLogger("PluginParent")

    def _load_internals(self):
        from pystatus.internal import PLUGINS
        self._log.debug("Loading internal plugins...")
        for plugin in PLUGINS:
            p = plugin()
            self._plugins[p.name.lower()] = p
            self._log.debug("Loaded %s [%s - %s]",
                            p.name, p.version, p.author)
        del PLUGINS

    def _load_externals(self, dirpath):
        search = re.compile(r"\.py$", re.IGNORECASE)
        files = filter(lambda f: (not f.startswith("__")
                                  and search.search(f)),
                       os.listdir(dirpath))
        for path in files:
            plugin_name = os.path.splitext(os.path.basename(path))[0]
            modname = "pystatus.plugin.%s" % plugin_name
            spec = importlib.util.spec_from_file_location(modname, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugin = mod.plugin()
            self._plugins[plugin.name.lower()] = plugin
            self._log.debug("Loaded %s [%s - %s]",
                            plugin.name, plugin.version, plugin.author)

    def load_plugins(self, dirpath):
        self._load_internals()
        if dirpath:
            self._log.info("Loading plugins from %s", dirpath)
            self._load_externals(dirpath)

    def instance(self, plugin, name, block, interval, options):
        plugin = plugin.lower()
        if plugin not in self._plugins:
            self._log.debug("Plugin %s not found", plugin)
            return None

        color = options.get("color")
        if isinstance(color, str):
            block.color = color
        background = options.get("background")
        if isinstance(background, str):
            block.background = background

        block.border = options.get("border")
        block.min_width = options.get("min_width")
        block.align = options.get("align")
        block.separator = options.get("separator")
        block.separator_block_width = options.get("separator_block_width")

        self._log.debug("Requesting new instance from %s with name %s",
                        plugin, name)
        inst = self._plugins[plugin].instance(name, block, interval, options)
        inst.start()

        self._instances["%s_%s" % (plugin, name.lower())] = inst

    def stop(self):
        for name, instance in self._instances.items():
            instance.stop(join=False)
        for name, instance in self._instances.items():
            self._log.debug("Waiting for instance %s to stop", instance.name)
            instance.join()

        for plugin_name, plugin in self._plugins.items():
            self._log.debug("Removing plugin %s", plugin.name)
            del plugin

        self._plugins = {}
        self._instances = {}
