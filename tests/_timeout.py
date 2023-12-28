# -*- coding: utf-8 -*-

import signal
from contextlib import ContextDecorator


def raise_timeout(signum, frame):
    raise TimeoutError()


class timeout(ContextDecorator):
    """Raises TimeoutError when the gien time in seconds elapsed.
    """

    def __init__(self, seconds):
        self._seconds = seconds

    def __enter__(self):
        if self._seconds:
            self._replace_alarm_handler()
            signal.setitimer(signal.ITIMER_REAL, self._seconds)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._seconds:
            self._restore_alarm_handler()
            signal.alarm(0)

    def _replace_alarm_handler(self):
        self._old_alarm_handler = signal.signal(signal.SIGALRM,
                                                raise_timeout)

    def _restore_alarm_handler(self):
        signal.signal(signal.SIGALRM, self._old_alarm_handler)
