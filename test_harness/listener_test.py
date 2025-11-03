from test_listener import TestListener
from test_result import TestResult


class AllListener(TestListener):
    def on_test_start(self, result: TestResult) -> None:
        """ Called immediately before a test method begins execution."""
        print("[DEBUG] Global on_test_start()")

    def on_test_success(self, result: TestResult) -> None:
        """ Called when a test method finishes successfully without raising
            errors. """
        print("[DEBUG] Global on_test_success()")

    def on_test_failure(self, result: TestResult) -> None:
        """ Called when a test method fails due to an exception or assertion
            error. """
        print("[DEBUG] Global on_test_failure()")

    def on_test_skipped(self, result: TestResult) -> None:
        """ Called when a test method is skipped (disabled or dependency
            failure). """
        print("[DEBUG] Global on_test_skipped()")
