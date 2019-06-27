import threading
import json
import logging
import io
from typing import Tuple


class Block:
    def __init__(self, name: str, instance: str):
        self._lock = threading.Lock()
        self._obj = {
            "name": name,
            "instance": instance,
        }

    @property
    def name(self) -> str:
        return self._obj["name"]

    @property
    def instance(self) -> str:
        return self._obj["instance"]

    @property
    def full_text(self) -> str:
        return self._obj["full_text"]

    @full_text.setter
    def full_text(self, value: str) -> None:
        self._obj["full_text"] = value

    @property
    def short_text(self) -> str:
        return self._obj["short_text"]

    @short_text.setter
    def short_text(self, value: str) -> None:
        self._obj["short_text"] = value

    @property
    def color(self) -> str:
        return self._obj["color"]

    @color.setter
    def color(self, value: str) -> None:
        self._obj["color"] = value

    @property
    def background(self) -> str:
        return self._obj["background"]

    @background.setter
    def background(self, value: str) -> None:
        self._obj["background"] = value

    @property
    def border(self) -> str:
        return self._obj["border"]

    @border.setter
    def border(self, value: str) -> None:
        self._obj["border"] = value

    @property
    def min_width(self) -> str:
        return self._obj["min_width"]

    @min_width.setter
    def min_width(self, value: str) -> None:
        self._obj["min_width"] = value

    @property
    def align(self) -> str:
        return self._obj["align"]

    @align.setter
    def align(self, value: str) -> None:
        self._obj["align"] = value

    @property
    def urgent(self) -> bool:
        return self._obj["urgent"]

    @urgent.setter
    def urgent(self, value: bool) -> None:
        self._obj["urgent"] = value

    @property
    def separator(self) -> bool:
        return self._obj["separator"]

    @separator.setter
    def separator(self, value: bool) -> None:
        self._obj["separator"] = value

    @property
    def separator_block_width(self) -> int:
        return self._obj["separator_block_width"]

    @separator_block_width.setter
    def separator_block_width(self, value: int) -> None:
        self._obj["separator_block_width"] = value

    @property
    def markup(self) -> str:
        return self._obj["markup"]

    @markup.setter
    def markup(self, value: str) -> None:
        self._obj["markup"] = value

    def lock(self) -> bool:
        return self._lock.acquire()

    __enter__ = lock

    def release(self) -> None:
        self._lock.release()

    def __exit__(self, t, v, tb) -> None:
        self.release()

    def __key(self) -> Tuple[str, str]:
        return (self.name, self.instance)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def __repr__(self) -> str:
        return "<Block %s_%s>" % (self["name"], self["instance"])


class BlockEncoder(json.JSONEncoder):
    def default(self, o):
        return {k: v for k, v in o._obj.items() if v}


class Statusline:
    def __init__(self, writer: io.IOBase, indent: int):
        self._is_open = False
        self._writer = writer
        self._indent = indent
        self._blocks = []
        self._lock = threading.Lock()
        self._log = logging.getLogger("Statusline")

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def writer(self) -> io.IOBase:
        return self._writer

    @property
    def indent(self) -> int:
        return self._indent

    @indent.setter
    def indent(self, value: int) -> None:
        self._indent = value

    def sendline(self) -> None:
        if not self.is_open:
            return

        with self._lock:
            # first lock all blocks
            for b in self._blocks:
                b.lock()

            try:
                if self._log.getEffectiveLevel == logging.DEBUG:
                    self._log.debug("Sending status line %s",
                                    json.dumps(self._blocks, cls=BlockEncoder))
                json.dump(self._blocks, self.writer,
                          indent=self.indent, cls=BlockEncoder)
                self.writer.flush()
            finally:
                # make sure every block is released
                for b in self._blocks:
                    b.release()

    def new_block(self, plugin: str, instance: str) -> Block:
        self._log.debug("Creating new block for %s:%s", plugin, instance)
        block = Block(plugin, instance)
        with self._lock:
            self._blocks.append(block)
        return block

    def start(self, version: int = 1, stop_signal: int = None,
              cont_signal: int = None, click_events: int = None) -> None:
        if self._is_open:
            self._log.warn("i3bar stream already started!")
            return
        obj = {"version": version}
        if stop_signal:
            obj["stop_signal"] = stop_signal
        if cont_signal:
            obj["cont_signal"] = cont_signal
        if click_events:
            obj["click_events"] = click_events
        self._log.info("Starting i3bar stream")
        self._log.debug("Sending protocol header %s", obj)
        json.dump(obj, self.writer, indent=self.indent)
        self.writer.write("[")
        self.writer.flush()
        self._is_open = True

    def stop(self) -> None:
        if not self.is_open:
            self._log.warn("i3bar stream already stopped!")
            return
        self._log.info("Stopping i3bar stream...")
        self.writer.write("]")
        self.writer.flush()
        self._is_open = False
