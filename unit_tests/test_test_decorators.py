import unittest
from executor_exceptions import TestFailure
from test_decorators import (test, listener, before_class, after_class,
                             before_method, after_method)
from test_status import TestStatus


# --- Unit tests ---
class TestDecorators(unittest.TestCase):

    def test_success_case(self):
        @test()
        def sample():
            return 42

        status, ex = sample()
        self.assertEqual(status, TestStatus.SUCCESS)
        self.assertIsNone(ex)
        self.assertTrue(sample.is_test)
        self.assertFalse(sample.run_in_parallel)
        self.assertTrue(sample.enabled)

    def test_failure_case_with_testfailure(self):
        @test()
        def sample():
            raise TestFailure("boom")

        status, ex = sample()
        self.assertEqual(status, TestStatus.FAILURE)
        self.assertIsInstance(ex, TestFailure)

    def test_failure_case_with_generic_exception(self):
        @test()
        def sample():
            raise ValueError("oops")

        status, ex = sample()
        self.assertEqual(status, TestStatus.FAILURE)
        self.assertIsInstance(ex, ValueError)

    def test_disabled_case(self):
        @test(enabled=False)
        def sample():
            return "should not run"

        status, ex = sample()
        self.assertEqual(status, TestStatus.SKIPPED)
        self.assertIsNone(ex)
        self.assertFalse(sample.enabled)

    def test_parallel_flag(self):
        @test(parallel=True)
        def sample():
            return "ok"

        self.assertTrue(sample.run_in_parallel)

    def test_listener_decorator(self):
        class DummyListener:
            def __init__(self):
                self.created = True

        @listener(DummyListener)
        class MyTest:
            pass

        self.assertTrue(hasattr(MyTest, "__listeners__"))
        self.assertIsInstance(MyTest.__listeners__[0], DummyListener)

    def test_before_class(self):
        def func(): pass
        decorated = before_class(func)
        self.assertTrue(hasattr(decorated, "is_before_class"))
        self.assertTrue(decorated.is_before_class)

    def test_after_class(self):
        def func(): pass
        decorated = after_class(func)
        self.assertTrue(hasattr(decorated, "is_after_class"))
        self.assertTrue(decorated.is_after_class)

    def test_before_method(self):
        def func(): pass
        decorated = before_method(func)
        self.assertTrue(hasattr(decorated, "is_before_method"))
        self.assertTrue(decorated.is_before_method)

    def test_after_method(self):
        def func(): pass
        decorated = after_method(func)
        self.assertTrue(hasattr(decorated, "is_after_method"))
        self.assertTrue(decorated.is_after_method)
