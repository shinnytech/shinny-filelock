import fcntl
import os
from contextlib import contextmanager


@contextmanager
def flocked(path, blocking=True, create_file=False, shared=False):
    """
    :param path: file path
    :param blocking: blocking lock, default True
    :param create_file: create file if not exists, default False
    :param shared: shared lock, default False
    """
    fd = -1
    try:
        fd_flags = os.O_RDONLY | os.O_NOCTTY
        if create_file:
            fd_flags |= os.O_CREAT
        fd = os.open(path, fd_flags)
        if fd == -1:
            raise ValueError()
        flags = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
        if not blocking:
            flags |= fcntl.LOCK_NB
        fcntl.flock(fd, flags)
        yield
    finally:
        if fd != -1:
            # close fd will release lock automatically
            os.close(fd)
