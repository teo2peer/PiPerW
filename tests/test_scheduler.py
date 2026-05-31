import threading
import time

from PiPerW.interfaces.scheduler_interface import Scheduler


def test_one_shot():
    done = threading.Event()
    Scheduler.at(time.time() + 0.05, done.set)
    assert done.wait(2.0)


def test_cancel():
    done = threading.Event()
    h = Scheduler.at(time.time() + 0.3, done.set)
    Scheduler.cancel(h)
    assert not done.wait(0.6)
