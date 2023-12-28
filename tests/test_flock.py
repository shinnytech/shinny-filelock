# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package
import unittest

from shinny_filelock import flocked

from ._timeout import timeout


class TestSimple(unittest.TestCase):

    def test_non_blocking_lock(self):
        local_path = "/tmp/test.lock"
        with flocked(local_path, blocking=False, create_file=True):
            try:
                with flocked(local_path, blocking=False, create_file=True):
                    pass
            except Exception as e:
                self.assertEqual(e.__class__, BlockingIOError)

    def test_blocking_lock(self):
        local_path = "/tmp/test-block.lock"
        with flocked(local_path, blocking=True, create_file=True):
            try:
                with timeout(2):
                    with flocked(local_path, blocking=True, create_file=True):
                        pass
            except Exception as e:
                self.assertEqual(e.__class__, TimeoutError)

    def test_blocking_with_non_blocking_lock(self):
        local_path = "/tmp/test-mix.lock"
        with flocked(local_path, blocking=True, create_file=True):
            try:
                with flocked(local_path, blocking=False, create_file=True):
                    pass
            except Exception as e:
                self.assertEqual(e.__class__, BlockingIOError)

    def test_file_not_exists(self):
        local_path = "/tmp/test-not-exists.lock"
        try:
            with flocked(local_path, blocking=True):
                pass
        except Exception as e:
            self.assertEqual(e.__class__, FileNotFoundError)


if __name__ == '__main__':
    unittest.main()
