import fcntl
import os
from contextlib import contextmanager


@contextmanager
def flocked(path, blocking=True, create_file=False, shared=False, inheritable=False):
    """
    :param path: file path
    :param blocking: blocking lock, default True
    :param create_file: create file if not exists, default False
    :param shared: shared lock, default False
    :param inheritable: inherit lock after exec, default False
    """
    fd_flags = os.O_RDONLY | os.O_NOCTTY
    fd_flags_with_create = fd_flags | os.O_CREAT
    # when stick bits set, os.O_CREAT will raise PermissionError
    try:
        fd = os.open(path, fd_flags_with_create if create_file else fd_flags)
    except PermissionError:
        # maybe file exists and sits in a directory with sticky bits
        fd = os.open(path, fd_flags)
    if fd == -1:
        raise ValueError()
    try:
        # default fd in non-inheritable. See PEP 446: https://peps.python.org/pep-0446/
        os.set_inheritable(fd, inheritable)
        flags = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
        if not blocking:
            flags |= fcntl.LOCK_NB
        fcntl.flock(fd, flags)
        try:
            yield
        finally:
            # early unlock in case someone is holding the fd(eg: fork without exec)
            # lock may also released due to fd closure when inheritable is true
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        # lock should already released
        # close fd to avoid resource leak
        os.close(fd)
