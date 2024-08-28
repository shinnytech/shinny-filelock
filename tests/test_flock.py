import subprocess
import unittest

from shinny_filelock import flocked

from ._timeout import timeout

local_path = "/tmp/shinny-filelock-test.lock"


class TestSimple(unittest.TestCase):

    def setUp(self):
        self.addCleanup(subprocess.check_call, ["sudo", "rm", "-f", local_path])

    def test_non_blocking_lock(self):
        # local_path = "/tmp/test.lock"
        with flocked(local_path, blocking=False, create_file=True):
            try:
                with flocked(local_path, blocking=False, create_file=True):
                    pass
            except Exception as e:
                self.assertEqual(e.__class__, BlockingIOError)

    def test_blocking_lock(self):
        with flocked(local_path, blocking=True, create_file=True):
            try:
                with timeout(2):
                    with flocked(local_path, blocking=True, create_file=True):
                        pass
            except Exception as e:
                self.assertEqual(e.__class__, TimeoutError)

    def test_blocking_with_non_blocking_lock(self):
        with flocked(local_path, blocking=True, create_file=True):
            try:
                with flocked(local_path, blocking=False, create_file=True):
                    pass
            except Exception as e:
                self.assertEqual(e.__class__, BlockingIOError)

    def test_file_not_exists(self):
        try:
            with flocked(local_path, blocking=True):
                pass
        except Exception as e:
            self.assertEqual(e.__class__, FileNotFoundError)

    def test_lock_with_file_created_by_another_user(self):
        # use sudo to create a file with sticky bits
        with open(local_path, "w"):
            subprocess.check_call(["sudo", "chown", "2222:3333", local_path])
        with flocked(local_path, blocking=True, create_file=True):
            pass


if __name__ == '__main__':
    unittest.main()
