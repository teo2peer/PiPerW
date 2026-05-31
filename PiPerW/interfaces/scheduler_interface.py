"""Scheduler — single daemon timer wheel.

One thread, N callbacks. Cheaper than N threading.Timer on Pi Zero.
Usage:
    from PiPerW.interfaces.scheduler_interface import Scheduler
    handle = Scheduler.every(2.0, callback)
    Scheduler.cancel(handle)
"""
import heapq
import itertools
import threading
import time
from abc import ABC, abstractmethod

from PiPerW.helpers import Log


class SchedulerInterface(ABC):
    @abstractmethod
    def every(self, seconds, callback, args=()): ...
    @abstractmethod
    def at(self, unix_ts, callback, args=()): ...
    @abstractmethod
    def cancel(self, handle): ...


class _Scheduler(SchedulerInterface):
    def __init__(self):
        self._heap = []
        self._cv = threading.Condition()
        self._counter = itertools.count()
        self._cancelled = set()
        self._thread = threading.Thread(target=self._run, daemon=True, name="Scheduler")
        self._stop = False
        self._thread.start()

    def _push(self, when, cb, args, repeat):
        with self._cv:
            handle = next(self._counter)
            heapq.heappush(self._heap, (when, handle, cb, args, repeat))
            self._cv.notify()
            return handle

    def every(self, seconds, callback, args=()):
        return self._push(time.time() + seconds, callback, args, seconds)

    def at(self, unix_ts, callback, args=()):
        return self._push(unix_ts, callback, args, None)

    def cancel(self, handle):
        with self._cv:
            self._cancelled.add(handle)
            self._cv.notify()

    def stop(self):
        with self._cv:
            self._stop = True
            self._cv.notify()

    def _run(self):
        while True:
            with self._cv:
                if self._stop:
                    return
                if not self._heap:
                    self._cv.wait()
                    continue
                when, handle, cb, args, repeat = self._heap[0]
                now = time.time()
                if when > now:
                    self._cv.wait(timeout=when - now)
                    continue
                heapq.heappop(self._heap)
                if handle in self._cancelled:
                    self._cancelled.discard(handle)
                    continue
            try:
                cb(*args)
            except Exception as e:
                Log.error(f"Scheduler callback failed: {e!r}")
            if repeat is not None:
                self._push(time.time() + repeat, cb, args, repeat)


Scheduler = _Scheduler()
