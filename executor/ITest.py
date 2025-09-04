import logging
import time
from executor_exceptions import TestFailure
from test_decorators import test
from test_executor import TestExecutor


# === Helper to assert failure inside tests ===
def fail_test(msg):
    """ Helper function to cause test to fail """
    raise TestFailure(msg)


# === Example Test Classes ===
class ExampleTest:
    """ Example tests """

    @test()
    def test_success(self):
        """ Test: (sequential) Test successful """
        print("test_success: This test passes")
        # nothing raised -> PASS
        time.sleep(7)

    @test(parallel=True)
    def test_failure(self):
        """ Test: (parallel) Test failed - fail_test """
        print("test_failure: This test fails intentionally")
        time.sleep(2)
        fail_test("Intentional failure")  # will be caught by decorator

    @test()
    def test_exception(self):
        """ Test: (sequential) Test failed - unexpected exception """
        print("This test raises an unexpected exception")
        time.sleep(4)
        x = 1 / 0  # will also be caught -> FAIL: division by zero
        print(f"X value: {x}")


LOGGING_DATETIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
LOGGING_DEFAULT_LOG_LEVEL = logging.DEBUG
LOGGING_LOG_FORMAT_STRING = "%(asctime)s [%(levelname)s] %(message)s"

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    log_format = logging.Formatter(LOGGING_LOG_FORMAT_STRING,
                                   LOGGING_DATETIME_FORMAT_STRING)
    console_stream = logging.StreamHandler()
    console_stream.setFormatter(log_format)
    logger.setLevel(LOGGING_DEFAULT_LOG_LEVEL)
    logger.addHandler(console_stream)

    executor: TestExecutor = TestExecutor(logger)

    results = executor.run_tests([ExampleTest])
    logger.debug("=== Test Results ===")

    for name, test_result in results.items():
        logger.info("[TEST STATUS] %s: %s [%s]",
                    name,
                    test_result.status,
                    test_result.caught_exception)
