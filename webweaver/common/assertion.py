"""
Self-contained assertion utilities for WebWeaver.

Supports both hard (fail-fast) and soft (collecting) assertions.

Designed to be framework-agnostic and reusable across:
- Studio playback
- Test executor
- Future automation modules
"""

from __future__ import annotations
from typing import Callable, Any
import logging


class AssertionFailure(AssertionError):
    """Raised when a hard assertion fails."""


class Assertions:
    """
    Assertion engine supporting hard and soft modes.

    Hard mode:
        - Raises AssertionFailure immediately.

    Soft mode:
        - Collects failures for later summarisation.
        - Does not raise until summarise() is called.
    """

    def __init__(self,
                 soft: bool = False,
                 logger: logging.Logger | None = None):
        self.soft = soft
        self.logger = logger
        self.failures: list[str] = []

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def assert_that(self, actual: Any, description: str | None = None) -> _AssertValue:
        return _AssertValue(self, actual, description)

    def summarise(self) -> None:
        """
        Raise a single AssertionError summarising all soft failures.
        Only meaningful when soft=True.
        """
        if not self.soft:
            return

        if not self.failures:
            return

        summary = "\n".join(f"  - {msg}" for msg in self.failures)
        raise AssertionError(f"Soft assertion failures:\n{summary}")

    # ---------------------------------------------------------
    # Internal failure handler
    # ---------------------------------------------------------

    def _handle_failure(self, message: str) -> None:
        if self.logger:
            self.logger.error(message)

        if self.soft:
            self.failures.append(message)
        else:
            raise AssertionFailure(message)


class _AssertValue:
    """
    Fluent assertion chain.
    Internal class – access via Assertions.assert_that().
    """

    def __init__(self,
                 parent: Assertions,
                 actual: Any,
                 description: str | None):
        self.parent = parent
        self.actual = actual
        self.description = description or ""

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------

    def _fail(self, msg: str) -> None:
        message = f"{self.description} {msg}".strip()
        self.parent._handle_failure(message)

    # ---------------------------------------------------------
    # Fluent matchers
    # ---------------------------------------------------------

    def is_equal_to(self, expected: Any) -> _AssertValue:
        if self.actual != expected:
            self._fail(f"expected {expected}, got {self.actual}")
        return self

    def is_not_equal_to(self, unexpected: Any) -> _AssertValue:
        if self.actual == unexpected:
            self._fail(f"expected not {unexpected}, but got it")
        return self

    def is_true(self) -> _AssertValue:
        if not self.actual:
            self._fail(f"expected True, got {self.actual}")
        return self

    def is_false(self) -> _AssertValue:
        if self.actual:
            self._fail(f"expected False, got {self.actual}")
        return self

    def is_none(self) -> _AssertValue:
        if self.actual is not None:
            self._fail(f"expected None, got {self.actual}")
        return self

    def is_not_none(self) -> _AssertValue:
        if self.actual is None:
            self._fail("expected a non-None value")
        return self

    def is_greater_than(self, value: Any) -> _AssertValue:
        if not self.actual > value:
            self._fail(f"expected > {value}, got {self.actual}")
        return self

    def is_less_than(self, value: Any) -> _AssertValue:
        if not self.actual < value:
            self._fail(f"expected < {value}, got {self.actual}")
        return self

    def contains(self, element: Any) -> _AssertValue:
        try:
            if element not in self.actual:
                self._fail(f"expected {self.actual} to contain {element}")
        except TypeError:
            self._fail(f"object of type {type(self.actual)} is not iterable")
        return self

    def is_in(self, collection: Any) -> _AssertValue:
        if self.actual not in collection:
            self._fail(f"expected {self.actual} to be in {collection}")
        return self

    def is_instance_of(self, cls: type) -> _AssertValue:
        if not isinstance(self.actual, cls):
            self._fail(
                f"expected instance of {cls.__name__}, "
                f"got {type(self.actual).__name__}"
            )
        return self

    def starts_with(self, prefix: str) -> _AssertValue:
        if not isinstance(self.actual, str):
            self._fail("starts_with() only applies to strings")
        elif not self.actual.startswith(prefix):
            self._fail(
                f"expected string starting with '{prefix}', "
                f"got '{self.actual}'"
            )
        return self

    def ends_with(self, suffix: str) -> _AssertValue:
        if not isinstance(self.actual, str):
            self._fail("ends_with() only applies to strings")
        elif not self.actual.endswith(suffix):
            self._fail(
                f"expected string ending with '{suffix}', "
                f"got '{self.actual}'"
            )
        return self

    def matches(self,
                predicate: Callable[[Any], bool],
                description: str | None = None) -> _AssertValue:
        try:
            if not predicate(self.actual):
                self._fail(description or "custom predicate failed")
        except Exception as ex:
            self._fail(f"predicate raised {ex}")
        return self
