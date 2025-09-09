import unittest
from test_result import TestResult
from test_status import TestStatus


# --- Unit tests ---
class TestTestResult(unittest.TestCase):

    def setUp(self):
        self.result = TestResult("test_method", "TestClass")

    def test_initialization(self):
        self.assertEqual(self.result.method_name, "test_method")
        self.assertEqual(self.result.test_class, "TestClass")
        self.assertEqual(self.result.status, TestStatus.CREATED)
        self.assertEqual(self.result.start_milliseconds, 0)
        self.assertEqual(self.result.end_milliseconds, 0)
        self.assertIsNone(self.result.caught_exception)

    def test_status_setter_and_getter(self):
        self.result.status = TestStatus.SUCCESS
        self.assertEqual(self.result.status, TestStatus.SUCCESS)

        self.result.status = TestStatus.FAILURE
        self.assertEqual(self.result.status, TestStatus.FAILURE)

        self.result.status = TestStatus.SKIPPED
        self.assertEqual(self.result.status, TestStatus.SKIPPED)

    def test_start_milliseconds(self):
        self.result.start_milliseconds = 123456
        self.assertEqual(self.result.start_milliseconds, 123456)

    def test_end_milliseconds(self):
        self.result.end_milliseconds = 654321
        self.assertEqual(self.result.end_milliseconds, 654321)

    def test_caught_exception_setter_and_getter(self):
        ex = ValueError("test error")
        self.result.caught_exception = ex
        self.assertIs(self.result.caught_exception, ex)
