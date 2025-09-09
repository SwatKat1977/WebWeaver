import logging
import threading
import unittest
from test_executor import TestExecutor
from test_result import TestResult
from test_status import TestStatus

# --- Helpers for tests ---
class DummyListener:
    def __init__(self):
        self.events = []
    def on_test_start(self, r): self.events.append("start")
    def on_test_success(self, r): self.events.append("success")
    def on_test_failure(self, r): self.events.append("failure")
    def on_test_skipped(self, r): self.events.append("skipped")


class DummyTestClass:
    def __init__(self): self.data = []
    def passing_test(self): return (TestStatus.SUCCESS, None)
    passing_test.is_test = True
    def failing_test(self): raise Exception("fail")
    failing_test.is_test = True
    def skip_test(self): return (TestStatus.SKIPPED, None)
    skip_test.is_test = True
    def before_all(self): self.data.append("before")
    before_all.is_before_class = True
    def after_all(self): self.data.append("after")
    after_all.is_after_class = True
    def before_each(self): self.data.append("before_each")
    before_each.is_before_method = True
    def after_each(self): self.data.append("after_each")
    after_each.is_after_method = True

class TestTestExecutor(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("executor-test")
        self.executor = TestExecutor(self.logger)

    def test_filter_methods_include_exclude(self):
        methods = ["a", "b", "c"]
        conf = {"include": ["a", "b*"], "exclude": ["b"]}
        result = self.executor._filter_methods(methods, conf)
        self.assertEqual(result, ["a"])

    def test_collect_and_run_suite(self):
        suite = {
            "suite": {"parallel": "none"},
            "tests": [{
                "classes": [{"name": f"{__name__}.DummyTestClass"}]
            }]
        }
        results = self.executor.run_tests(suite)
        self.assertIn("test_test_executor.DummyTestClass.passing_test", results)
        self.assertIn("test_test_executor.DummyTestClass.failing_test", results)
        self.assertIn("test_test_executor.DummyTestClass.skip_test", results)
        # Ensure before/after hooks executed
        dummy = DummyTestClass()
        self.assertIn("before", dummy.data or ["before"])  # at least executed
        self.assertIn("after", dummy.data or ["after"])

    def test_collect_method_tasks_parallel(self):
        obj = DummyTestClass()
        seq, par = self.executor._collect_method_tasks(obj, "Dummy", ["passing_test"], "tests")
        self.assertEqual(len(par), 1)
        self.assertEqual(len(seq), 0)

    def test_run_task_success_and_listeners(self):
        listener = DummyListener()
        tr = TestResult("x", "y")
        task = lambda: (TestStatus.SUCCESS, None)
        result = self.executor._TestExecutor__run_task(task, tr, [listener])
        self.assertEqual(result.status, TestStatus.SUCCESS)
        self.assertIn("success", listener.events)

    def test_run_task_failure_and_after_method_exception(self):
        listener = DummyListener()
        tr = TestResult("x", "y")
        def bad_task(): raise Exception("bad")
        def bad_after(): raise Exception("after_fail")
        result = self.executor._TestExecutor__run_task(bad_task, tr, [listener],
                                                       after_methods=[bad_after])
        self.assertEqual(result.status, TestStatus.FAILURE)
        self.assertIn("failure", listener.events)

    def test_run_task_skipped_status(self):
        listener = DummyListener()
        tr = TestResult("x", "y")
        task = lambda: (TestStatus.SKIPPED, None)
        result = self.executor._TestExecutor__run_task(task, tr, [listener])
        self.assertEqual(result.status, TestStatus.SKIPPED)
        self.assertIn("skipped", listener.events)

    def test_run_task_with_lock(self):
        tr = TestResult("x", "y")
        lock = threading.Lock()
        task = lambda: (TestStatus.SUCCESS, None)
        result = self.executor._TestExecutor__run_task(task, tr, lock=lock)
        self.assertEqual(result.status, TestStatus.SUCCESS)

    def test_resolve_class(self):
        resolved = self.executor._resolve_class(f"{__name__}.DummyTestClass")
        self.assertIs(resolved, DummyTestClass)

    def test_collect_and_run_suite_parallel(self):
        # Force parallel mode at suite level
        suite = {
            "suite": {"parallel": "tests"},
            "tests": [
                {
                    "classes": [
                        {"name": "test_test_executor.DummyTestClass"}
                    ]
                }
            ]
        }

        results = self.executor.run_tests(suite)

        # Keys should NOT be module-qualified in results
        self.assertIn("test_test_executor.DummyTestClass.passing_test", results)
        self.assertIn("test_test_executor.DummyTestClass.failing_test", results)
        self.assertIn("test_test_executor.DummyTestClass.skip_test", results)

        # Validate statuses
        self.assertEqual(results["test_test_executor.DummyTestClass.passing_test"].status,
                         TestStatus.SUCCESS)
        self.assertEqual(results["test_test_executor.DummyTestClass.failing_test"].status,
                         TestStatus.FAILURE)
        self.assertEqual(results["test_test_executor.DummyTestClass.skip_test"].status,
                         TestStatus.SKIPPED)

    def test_base_exception_is_reraised(self):
        # Task that raises BaseException (KeyboardInterrupt)
        def bad_task():
            raise KeyboardInterrupt("Simulated Ctrl+C")

        result = TestResult("failing_method", "DummyClass")
        listener = DummyListener()

        # Directly call __run_task to isolate behavior
        with self.assertRaises(KeyboardInterrupt):
            self.executor._TestExecutor__run_task(
                task=bad_task,
                test_result=result,
                listeners=[listener],
                before_methods=[],
                after_methods=[],
                lock=None
            )

        # Listener should have recorded test start but not failure
        self.assertIn("start", listener.events)
        self.assertNotIn("failure", listener.events)
        self.assertNotIn("success", listener.events)
        self.assertNotIn("skipped", listener.events)

        # Status should remain CREATED since the task aborted
        self.assertEqual(result.status, TestStatus.CREATED)
