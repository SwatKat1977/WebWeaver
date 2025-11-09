"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025 SwatKat1977

    This program is free software : you can redistribute it and /or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import logging


class AssertionFailure(AssertionError):
    """Raised when a hard assertion fails."""


class AssumptionFailure(AssertionError):
    """Raised when a soft (assume) assertion fails."""


class AssertionContext:
    """
    Shared base for both hard and soft assertions.

    Provides two main entry points:
        - assert_that(value, description): performs hard assertions (raise
          immediately)
        - assume_that(value, description): performs soft assertions (collect
          for later)
    """

    def __init__(self, logger: logging.Logger | None = None):
        """
        Initialize the assertion context.

        Args:
            logger: Optional logger instance. If not provided, a default
                    'webweaver.Assertions' logger is used.
        """
        self.logger = logger or logging.getLogger("webweaver.Assertions")

    def assert_that(self, actual, description=None):
        """
        Create a hard assertion chain for the given value.

        Args:
            actual: The actual value under test.
            description: Optional human-readable description of the assertion.

        Returns:
            _AssertValue: A fluent assertion chain configured for hard assertion mode.
        """
        return _AssertValue(self,
                            actual,
                            description,
                            hard=True,
                            assume=False)

    def assume_that(self, actual, description=None):
        """
        Create a soft assertion chain for the given value.

        Unlike hard assertions, failures are logged and collected rather than raised
        immediately, allowing test execution to continue.

        Args:
            actual: The actual value under test.
            description: Optional human-readable description of the assertion.

        Returns:
            _AssertValue: A fluent assertion chain configured for soft assertion mode.
        """
        return _AssertValue(self,
                            actual,
                            description,
                            hard=False,
                            assume=True)


class SoftAssertions(AssertionContext):
    """
    Collects soft assumption failures for later summarization.
    Soft and Hard Assertions for WebWeaver tests.

    Provides AssertJ-style fluent assertions:
        self.assert_that(value, "desc").is_equal_to(expected)  # hard (raises)
        self.assume_that(value, "desc").is_equal_to(expected)  # soft (collects)
    """

    def __init__(self, logger: logging.Logger | None = None):
        """
        Initialize a SoftAssertions context.

        Args:
            logger: Optional logger instance for reporting soft failures.
        """
        super().__init__(logger)
        self.failures: list[str] = []

    def add_failure(self, message: str):
        """
        Record a soft failure for later summarization.

        Args:
            message: The failure message to store.
        """
        self.failures.append(message)
        self.logger.error(f"[Assume] {message}")

    def summarise(self):
        """
        Summarize all collected soft assumption failures.

        Raises:
            AssertionError: If one or more soft assumptions failed.
        """
        if not self.failures:
            self.logger.debug("All soft assumptions passed.")
            return
        summary = "\n".join(f"  - {msg}" for msg in self.failures)
        raise AssertionError(f"Soft assumption failures:\n{summary}")


class _AssertValue:
    """
    Fluent chain for both hard and soft assertions.

    Each method in this class performs a specific type of assertion
    (e.g., equality, comparison, type checking) and returns `self`
    for fluent chaining.

    Internal class; users should access it via AssertionContext methods.
    """

    def __init__(self,
                 parent: AssertionContext,
                 actual,
                 description,
                 hard: bool,
                 assume: bool = False):
        self.parent = parent
        self.actual = actual
        self.description = description or ""
        self.hard = hard
        self.assume = assume
        """
        Initialize an assertion chain.

        Args:
            parent: The parent assertion context (hard or soft).
            actual: The value being tested.
            description: Optional text describing the assertion.
            hard: Whether this is a hard (raise immediately) assertion.
            assume: Whether this is a soft assumption instead of a true assertion.
        """

    # --- Assertion primitives ---
    def _fail(self, msg: str):
        """
        Handle assertion failure based on context (hard or soft).

        Logs the message and either raises an exception or records the failure.

        Args:
            msg: Description of the failed condition.

        Raises:
            AssertionFailure or AssumptionFailure for hard assertions,
            or records the failure for soft ones.
        """
        message = f"{self.description} {msg}".strip()

        # Case 1: soft assume (collect and continue, no raise)
        if self.assume and not self.hard:
            self.parent.logger.warning(f"[Assume] {message}")
            # if parent has SoftAssertions collector, record it
            if hasattr(self.parent, "soft_collector"):
                self.parent.soft_collector.add_failure(message)
            return

        # Case 2: hard assume (immediate skip)
        if self.assume and self.hard:
            self.parent.logger.warning(f"[Assume] {message}")
            raise AssumptionFailure(message)

        # Case 3: hard assert (immediate fail)
        if self.hard:
            self.parent.logger.error(f"[Assert] {message}")
            raise AssertionFailure(message)

        # Case 4: default soft collector (e.g., self.softly.assume_that())
        assert isinstance(self.parent, SoftAssertions)
        self.parent.add_failure(message)

    # --- Fluent matchers ---
    def is_equal_to(self, expected):
        """Assert that the actual value equals the expected value."""
        if self.actual != expected:
            self._fail(f"expected {expected}, got {self.actual}")
        return self

    def is_not_equal_to(self, unexpected):
        """Assert that the actual value does not equal the unexpected value."""
        if self.actual == unexpected:
            self._fail(f"expected not {unexpected}, but got it")
        return self

    def is_true(self):
        """Assert that the actual value is True."""
        if not self.actual:
            self._fail(f"expected True, got {self.actual}")
        return self

    def is_false(self):
        """Assert that the actual value is False."""
        if self.actual:
            self._fail(f"expected False, got {self.actual}")
        return self

    def is_not_none(self):
        """Assert that the actual value is not None."""
        if self.actual is None:
            self._fail("expected a non-None value")
        return self

    def is_none(self):
        """Assert that the actual value is None."""
        if self.actual is not None:
            self._fail(f"expected None, got {self.actual}")
        return self

    def is_greater_than(self, value):
        """Assert that the actual value is greater than the given value."""
        if not self.actual > value:
            self._fail(f"expected > {value}, got {self.actual}")
        return self

    def is_less_than(self, value):
        """Assert that the actual value is less than the given value."""
        if not self.actual < value:
            self._fail(f"expected < {value}, got {self.actual}")
        return self

    def contains(self, element):
        """Assert that the actual value (iterable) contains the given element."""
        try:
            if element not in self.actual:
                self._fail(f"expected {self.actual} to contain {element}")
        except TypeError:
            self._fail(f"object of type {type(self.actual)} is not iterable")
        return self

    def matches(self, predicate, description=None):
        """
        Assert that a custom predicate returns True for the actual value.

        Args:
            predicate: A callable that takes the actual value and returns a bool.
            description: Optional custom failure message.
        """
        try:
            if not predicate(self.actual):
                self._fail(description or "custom predicate failed")
        except Exception as ex:
            self._fail(f"predicate raised {ex}")
        return self

    def is_in(self, collection):
        """Assert that the actual value is a member of the given collection."""
        if self.actual not in collection:
            self._fail(f"expected {self.actual} to be in {collection}")
        return self

    def is_instance_of(self, cls):
        """Assert that the actual value is an instance of the given class."""
        if not isinstance(self.actual, cls):
            self._fail(f"expected instance of {cls.__name__}, got {type(self.actual).__name__}")
        return self

    def starts_with(self, prefix: str):
        """Assert that the actual string starts with the given prefix."""
        if not isinstance(self.actual, str):
            self._fail("starts_with() only applies to strings")
        elif not self.actual.startswith(prefix):
            self._fail(f"expected string starting with '{prefix}', got '{self.actual}'")
        return self

    def ends_with(self, suffix: str):
        """Assert that the actual string ends with the given suffix."""
        if not isinstance(self.actual, str):
            self._fail("ends_with() only applies to strings")
        elif not self.actual.endswith(suffix):
            self._fail(f"expected string ending with '{suffix}', got '{self.actual}'")
        return self
