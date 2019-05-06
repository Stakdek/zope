import time
import threading
import unittest


class Mythread(threading.Thread):
    # The default includes a timestamp when the thread was started.
    def __repr__(self):
        return "<Thread(%s)>" % self.name


class TestNewThreadsReporting(unittest.TestCase):
    def test_leave_thread_behind(self):
        Mythread(name='t1', target=time.sleep, args=[1]).start()
