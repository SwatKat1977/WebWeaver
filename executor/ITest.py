import enum
from test_decorators import test



import functools
from concurrent.futures import ThreadPoolExecutor
from executor_exceptions import TestFailure

# === Helper to assert failure inside tests ===
def fail_test(msg):
    raise TestFailure(msg)

# === Example Test Classes ===
class ExampleTest:
    @test()
    def test_success(self):
        print("This test passes")
        # nothing raised -> PASS

    @test()
    def test_failure(self):
        print("This test fails intentionally")
        fail_test("Intentional failure")  # will be caught by decorator

    @test()
    def test_exception(self):
        print("This test raises an unexpected exception")
        x = 1 / 0  # will also be caught -> FAIL: division by zero

"""
# === Runner ===
def run_tests(test_classes, max_workers=3):
    sequential_tasks = []
    parallel_tasks = []
    results = {}

    for cls in test_classes:
        obj = cls()

        for attr_name in dir(obj):
            method = getattr(obj, attr_name)

            if callable(method) and getattr(method, "is_test", False):
                task_name = f"{cls.__name__}.{attr_name}"

                if method.run_in_parallel:
                    parallel_tasks.append((task_name,
                                           functools.partial(method)))

                else:
                    sequential_tasks.append((task_name, method))

    print("=== Running Sequential Tests ===")
    for name, task in sequential_tasks:
        results[name] = task()

    print("\n=== Running Parallel Tests ===")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(task): name for name, task in parallel_tasks}
        for f in future_map:
            results[future_map[f]] = f.result()

    return results
"""

import logging
from test_executor import TestExecutor


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
        logger.debug("[TEST STATUS] %s: %s",
                     name,
                     test_result.status)
