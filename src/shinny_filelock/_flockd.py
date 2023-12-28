import fcntl
import os
from contextlib import contextmanager


@contextmanager
def flocked(path, blocking=False, create_file=False):
    """
    :param path: file path
    :param blocking: blocking lock
    :param create_file: create file if not exists
    """
    fd = -1
    try:
        fd_flags = os.O_RDONLY | os.O_NOCTTY
        if create_file:
            fd_flags |= os.O_CREAT
        fd = os.open(path, fd_flags)
        if fd == -1:
            raise ValueError()
        try:
            flags = fcntl.LOCK_EX
            if not blocking:
                flags |= fcntl.LOCK_NB
            fcntl.flock(fd, flags)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        if fd != -1:
            os.close(fd)
