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
    pass


class AssumptionFailure(AssertionError):
    """Raised when a soft (assume) assertion fails."""
    pass


class AssertionContext:
    """Shared base for both hard and soft assertions."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("webweaver.Assertions")

    def assert_that(self, actual, description=None):
        """Hard assertion: fails immediately."""
        return _AssertValue(self,
                            actual,
                            description,
                            hard=True,
                            assume=False)

    def assume_that(self, actual, description=None):
        """Soft assertion: collects and reports later."""
        return _AssertValue(self,
                            actual,
                            description,
                            hard=True,
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
        super().__init__(logger)
        self.failures: list[str] = []

    def add_failure(self, message: str):
        """Record a soft failure."""
        self.failures.append(message)
        self.logger.error(f"[Assume] {message}")

    def summarise(self):
        """Raise a combined error if any assumptions failed."""
        if not self.failures:
            self.logger.debug("All soft assumptions passed.")
            return
        summary = "\n".join(f"  - {msg}" for msg in self.failures)
        raise AssertionError(f"Soft assumption failures:\n{summary}")


class _AssertValue:
    """Fluent chain for both hard and soft assertions."""

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

    # --- Assertion primitives ---
    def _fail(self, msg: str):
        message = f"{self.description} {msg}".strip()

        if self.assume:
            self.parent.logger.warning(f"[Assume] {message}")
            raise AssumptionFailure(message)

        elif self.hard:
            self.parent.logger.error(f"[Assert] {message}")
            raise AssertionFailure(message)

        else:
            # Soft (collect) mode
            assert isinstance(self.parent, SoftAssertions)
            self.parent.add_failure(message)

    # --- Fluent matchers ---
    def is_equal_to(self, expected):
        if self.actual != expected:
            self._fail(f"expected {expected}, got {self.actual}")
        return self

    def is_not_equal_to(self, unexpected):
        if self.actual == unexpected:
            self._fail(f"expected not {unexpected}, but got it")
        return self

    def is_true(self):
        if not self.actual:
            self._fail(f"expected True, got {self.actual}")
        return self

    def is_false(self):
        if self.actual:
            self._fail(f"expected False, got {self.actual}")
        return self

    def is_not_none(self):
        if self.actual is None:
            self._fail("expected a non-None value")
        return self

    def is_none(self):
        if self.actual is not None:
            self._fail(f"expected None, got {self.actual}")
        return self

    def is_greater_than(self, value):
        if not (self.actual > value):
            self._fail(f"expected > {value}, got {self.actual}")
        return self

    def is_less_than(self, value):
        if not (self.actual < value):
            self._fail(f"expected < {value}, got {self.actual}")
        return self

    def contains(self, element):
        try:
            if element not in self.actual:
                self._fail(f"expected {self.actual} to contain {element}")
        except TypeError:
            self._fail(f"object of type {type(self.actual)} is not iterable")
        return self

    def matches(self, predicate, description=None):
        """Custom match: pass a lambda and optional description."""
        try:
            if not predicate(self.actual):
                self._fail(description or "custom predicate failed")
        except Exception as ex:
            self._fail(f"predicate raised {ex}")
        return self

    def is_in(self, collection):
        if self.actual not in collection:
            self._fail(f"expected {self.actual} to be in {collection}")
        return self

    def is_instance_of(self, cls):
        if not isinstance(self.actual, cls):
            self._fail(f"expected instance of {cls.__name__}, got {type(self.actual).__name__}")
        return self

    def starts_with(self, prefix: str):
        if not isinstance(self.actual, str):
            self._fail("starts_with() only applies to strings")
        elif not self.actual.startswith(prefix):
            self._fail(f"expected string starting with '{prefix}', got '{self.actual}'")
        return self

    def ends_with(self, suffix: str):
        if not isinstance(self.actual, str):
            self._fail("ends_with() only applies to strings")
        elif not self.actual.endswith(suffix):
            self._fail(f"expected string ending with '{suffix}', got '{self.actual}'")
        return self
