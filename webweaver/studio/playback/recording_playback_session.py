"""
This source file is part of Web Weaver
For the latest info, see https://github.com/SwatKat1977/WebWeaver

Copyright 2025-2026 Webweaver Development Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
from dataclasses import dataclass
import json
from logging import Logger
import threading
import typing
import wx
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webweaver.studio.api_client import ApiClient
from webweaver.studio.browsing.studio_browser import (PlaybackStepResult,
                                                      StudioBrowser)
from webweaver.studio.persistence.recording_document import RestApiBodyType
from webweaver.studio.playback.playback_context import PlaybackContext, PlaybackVariableError
from webweaver.studio.recording.recording import Recording
from webweaver.common.assertion import Assertions, AssertionFailure
from webweaver.common.assertion_operator import (AssertionOperator,
                                                 ASSERTION_NUMERICAL_OPERATORS,
                                                 ASSERTION_STRING_OPERATORS,
                                                 ASSERTION_BOOLEAN_OPERATORS,
                                                 ASSERTION_EXISTENCE_OPERATORS)


@dataclass
class PlaybackCallbackEvents:
    """
    Container for optional playback lifecycle callbacks.

    This dataclass groups together a set of callback functions that can be
    provided by the UI or other controlling code to receive notifications
    about playback progress and results.

    All callbacks are optional. If a callback is None, it is simply not called.

    Callbacks:

    - on_step_started(index: int) -> None
        Called when playback begins executing a step.

    - on_step_passed(index: int) -> None
        Called when a step completes successfully.

    - on_step_failed(index: int, reason: str) -> None
        Called when a step fails. The reason string contains a human-readable
        error message describing the failure.

    - on_playback_finished() -> None
        Called once playback has finished, either because all steps completed
        or because playback stopped due to a failure.
    """
    on_step_started: typing.Callable[[int], None] = None
    on_step_passed: typing.Callable[[int], None] = None
    on_step_failed: typing.Callable[[int], None] = None
    on_playback_finished: typing.Callable[[int], None] = None


class RecordingPlaybackSession:
    """
    Executes a recorded WebWeaver recording step-by-step using a StudioBrowser.

    A RecordingPlaybackSession represents a single playback run over a
    Recording. It maintains an instruction pointer into the recording's event
    list and exposes a simple control surface for starting, stopping, and
    stepping through events one at a time.

    This class is intentionally stateful and UI-friendly: it is designed to be
    driven by toolbar actions such as Play, Step, Pause, and Stop, and to report
    failures immediately when an event cannot be executed.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger):
        """
        Create a new playback session for the given recording.

        :param browser: StudioBrowser instance used to execute playback actions.
        :param recording: The Recording to be played back.
        :param logger: Base logger used for emitting playback diagnostics.
        """
        self._browser = browser
        self._recording = recording
        self._index = 0
        self._running = False
        self._logger = logger.getChild(__name__)
        self.callback_events = PlaybackCallbackEvents()
        self._context = PlaybackContext(self._browser.raw)
        self._hard_assert: Assertions = Assertions(soft=False,
                                                   logger=self._logger)
        self._soft_assert: Assertions = Assertions(soft=True,
                                                   logger=self._logger)
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        """
        Start playback from the beginning of the recording.

        This resets the internal instruction pointer to the first event and
        marks the session as running. No events are executed until step() is
        called.
        """
        self._running = True
        self._index = 0
        self._context.clear()

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._playback_loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        """
        Stop playback.

        This halts the session and prevents any further events from being
        executed until start() is called again.
        """
        self._running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive() \
                and threading.current_thread() != self._thread:
            self._thread.join(timeout=2)

            if self._thread.is_alive():
                self._logger.warning("Playback thread did not stop in time")

    def step(self) -> bool:
        """
        Execute the next event in the recording.

        This method executes exactly one recorded event and advances the
        internal instruction pointer if the event succeeds.

        If playback is not currently running, or if the end of the recording
        has been reached, this method returns False and performs no action.

        If the event fails, playback is stopped and False is returned.

        :return: True if an event was executed successfully, False otherwise.
        """
        if not self._running:
            return False

        if self._index >= len(self._recording.events):
            self.stop()
            if self.callback_events.on_playback_finished:
                wx.CallAfter(self.callback_events.on_playback_finished)

            return False

        current_index = self._index

        if self.callback_events.on_step_started:
            wx.CallAfter(self.callback_events.on_step_started, current_index)

        event = self._recording.events[current_index]
        result = self._execute_event(event)

        if not result.ok:
            if self.callback_events.on_step_failed:
                wx.CallAfter(self.callback_events.on_step_failed,
                             current_index,
                             result.error)

            self.stop()
            return False

        # success
        if self.callback_events.on_step_passed:
            wx.CallAfter(self.callback_events.on_step_passed, current_index)

        self._index += 1

        return True

    def _playback_loop(self):
        while self._running and not self._stop_event.is_set():
            if self._stop_event.is_set():
                break

            still_running = self.step()

            if not still_running:
                break

    def _execute_event(self, event: dict):
        """
        Execute a single recorded event and return a PlaybackStepResult.

        This method is crash-safe: any exception raised during execution is
        caught and converted into a PlaybackStepResult failure.
        """
        # pylint: disable=too-many-return-statements, too-many-branches

        try:
            event_type = event.get("type")
            payload = event.get("payload", {})

            if event_type == 'assert':
                self._logger.debug("[PLAYBACK EVENT] Assert: %s", payload)
                return self._perform_assert_playback(payload)

            if event_type == "dom.check":
                self._logger.debug("[PLAYBACK EVENT] Check: %s", payload)
                return self._browser.playback_check(payload)

            if event_type == "dom.click":
                self._logger.debug("[PLAYBACK EVENT] Button: %s", payload)
                return self._browser.playback_click(payload)

            if event_type == "dom.get":
                self._logger.debug("[PLAYBACK EVENT] Element Get: %s", payload)
                return self._browser.playback_get(payload, self._context)

            if event_type == "dom.select":
                return self._perform_dom_select(payload)

            if event_type == "dom.type":
                return self._perform_dom_type(payload)

            if event_type == "nav.goto":
                url: str = payload.get("url")
                self._logger.debug("[PLAYBACK EVENT] Navigate to '%s'", url)

                try:
                    self._browser.open_page(url)
                except selenium.common.exceptions.WebDriverException:
                    return PlaybackStepResult.fail(f"Unable to navigate to '{url}'")

                return PlaybackStepResult.success()

            if event_type == "rest_api":
                self._logger.debug("[PLAYBACK EVENT] REST API: %s ", payload)
                return self._perform_rest_api(event)

            if event_type == "scroll":
                self._logger.debug("[PLAYBACK EVENT] Scroll: %s ", payload)
                self._perform_page_scroll(event)
                return PlaybackStepResult.success()

            if event_type == "sendkeys":
                self._logger.debug("[PLAYBACK EVENT] Sendkeys: %s", payload)
                return self._perform_sendkeys(event)

            if event_type == "user_variable":
                self._logger.debug("[PLAYBACK EVENT] User Variable: %s", payload)
                return self._playback_user_variable(payload.get("name"),
                                                    payload.get("value"))

            if event_type == "wait":
                self._logger.debug("[PLAYBACK EVENT] Wait: %s ms", payload)
                return self._perform_wait(event)

            self._logger.debug("[PLAYBACK EVENT] Unknown event: %s", event_type)
            return PlaybackStepResult.success()

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Absolute last-resort safety net
            self._logger.exception("Playback event crashed")
            return PlaybackStepResult.fail(str(e))

    def _perform_dom_select(self, payload):
        updated_payload = payload.copy()
        xpath = updated_payload.get("xpath", "")
        value = updated_payload.get("value", "")

        try:
            xpath = self._context.resolve_template(xpath)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"DOM Select xpath variable '{xpath}' is not defined")

        try:
            value = self._context.resolve_template(value)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"DOM Select value variable '{value}' is not defined")

        updated_payload["xpath"] = xpath
        updated_payload["value"] = value

        self._logger.debug("[PLAYBACK EVENT] Text: %s", updated_payload)
        return self._browser.playback_select(updated_payload)

    def _perform_dom_type(self, payload):
        updated_payload = payload.copy()
        xpath = updated_payload.get("xpath", "")
        value = updated_payload.get("value", "")

        try:
            xpath = self._context.resolve_template(xpath)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"DOM Type xpath variable '{xpath}' is not defined")

        try:
            value = self._context.resolve_template(value)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"DOM Type value variable '{value}' is not defined")

        updated_payload["xpath"] = xpath
        updated_payload["value"] = value

        self._logger.debug("[PLAYBACK EVENT] Type: %s", updated_payload)
        return self._browser.playback_type(updated_payload)

    def _perform_wait(self, event):
        payload = event.get("payload", {})
        duration = payload.get("duration_ms")

        interrupted = self._stop_event.wait(duration / 1000)
        if interrupted:
            return PlaybackStepResult.fail("Playback stopped")

        return PlaybackStepResult.success()

    def _perform_rest_api(self, event):
        # pylint: disable=too-many-return-statements
        payload = event.get("payload", {})
        call_type = payload.get("call_type")
        base_url = payload.get("base_url")
        rest_call = payload.get("rest_call")
        body_type = payload.get("body_type", RestApiBodyType.TEXT.value)
        call_body = payload.get("body")
        output_name = payload.get("output_variable")

        try:
            base_url = self._context.resolve_template(base_url)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"REST API base url variable '{base_url}' is not defined")

        try:
            rest_call = self._context.resolve_template(rest_call)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"REST API call variable '{rest_call}' is not defined")

        if call_body:
            try:
                call_body = self._context.resolve_template(call_body)
            except PlaybackVariableError:
                return PlaybackStepResult.fail(
                    f"REST API body variable '{call_body}' is not defined")

        api_client = ApiClient()

        body_type = RestApiBodyType[body_type.upper()]
        call_url = f"{base_url}{rest_call}"

        try:
            # -----------------------------
            # Perform HTTP call
            # -----------------------------
            if call_type == "get":
                response = asyncio.run(api_client.call_api_get(url=call_url))

            elif call_type == "post":
                response = asyncio.run(api_client.call_api_post(
                    url=call_url, body=call_body, body_type=body_type))

                print(f"Response: Status = {response.status_code} | Body: {response.body}")

            elif call_type == "delete":
                response = asyncio.run(api_client.call_api_delete(url=call_url))

            else:
                return PlaybackStepResult.fail(
                    f"Unknown REST call type '{call_type}'")

            # -----------------------------
            # Store result in context
            # -----------------------------
            result = {
                "status": response.status_code,
                "ok": 200 <= response.status_code < 300,
                "body": response.body,
                "headers": getattr(response, "headers", {})
            }

            if output_name:
                self._context.set_variable(output_name, result)

            if response.status_code == 0:
                error_msg = getattr(response, "error", None)

                if not error_msg:
                    error_msg = "REST call failed before receiving an HTTP response"

                return PlaybackStepResult.fail(error_msg)

            self._logger.info("REST API status=%s error=%s",
                              response.status_code,
                              getattr(response, "error", None))

            return PlaybackStepResult.success()

        except (RuntimeError, OSError, TimeoutError) as e:
            # RuntimeError -> event loop issues
            # OSError / TimeoutError -> network-related failures
            return PlaybackStepResult.fail(str(e))

    def _perform_page_scroll(self, event):
        payload = event.get("payload", {})
        scroll_type = payload.get("scroll_type")
        scroll_x = payload.get("x_scroll")
        scroll_y = payload.get("y_scroll")

        # Scroll to the bottom of the page.
        if scroll_type == "bottom":
            self._browser.scroll_to_bottom()

        # Scroll to the top of the page.
        elif scroll_type == "top":
            self._browser.scroll_to_top()

        # Scroll a specific distance (in pixels).
        elif scroll_type == "custom":
            self._browser.scroll_to(int(scroll_x), int(scroll_y))

    def _perform_assert_playback(self, payload):
        operator = payload.get("operator")
        soft_assert: bool = bool(payload.get("soft_assert"))
        left_value = payload.get("left_value")
        right_value = payload.get("right_value")

        try:
            left_value = self._context.resolve_template(left_value)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"Assert left variable '{left_value}' is not defined")

        try:
            right_value = self._context.resolve_template(right_value)
        except PlaybackVariableError:
            return PlaybackStepResult.fail(
                f"Assert right variable '{left_value}' is not defined")

        operator_enum = AssertionOperator(operator)

        asserter = self._soft_assert if soft_assert else self._hard_assert

        try:
            # Process numerical assertion operators
            if operator_enum in ASSERTION_NUMERICAL_OPERATORS:
                self._playback_numerical_operator(left_value,
                                                  right_value,
                                                  operator_enum,
                                                  asserter)

            if operator_enum in ASSERTION_STRING_OPERATORS:
                self._playback_string_assertion(left_value,
                                                right_value,
                                                operator_enum,
                                                asserter)

            if operator_enum in ASSERTION_BOOLEAN_OPERATORS:
                self._playback_boolean_assertion(left_value,
                                                 operator_enum,
                                                 asserter)

            if operator_enum in ASSERTION_EXISTENCE_OPERATORS:
                self._playback_existence_assertion(left_value,
                                                   operator_enum,
                                                   asserter)

        except AssertionFailure as ex:
            assert_msg: str = str(ex)
            return PlaybackStepResult.fail(assert_msg)

        return PlaybackStepResult.success()

    def _playback_numerical_operator(self,
                                     left_value,
                                     right_value,
                                     operator: AssertionOperator,
                                     asserter):

        if operator == AssertionOperator.EQUALS:
            asserter.assert_that(left_value).is_equal_to(right_value)

        elif operator == AssertionOperator.NOT_EQUALS:
            asserter.assert_that(left_value).is_not_equal_to(right_value)

        elif operator == AssertionOperator.GREATER_THAN:
            try:
                left_value = float(left_value)
                right_value = float(right_value)

            except ValueError as ex:
                raise AssertionFailure(
                    "Numeric comparison requires numeric values") from ex

            asserter.assert_that(left_value).is_greater_than(right_value)

        elif operator == AssertionOperator.LESS_THAN:
            try:
                left_value = float(left_value)
                right_value = float(right_value)

            except ValueError as ex:
                raise AssertionFailure(
                    "Numeric comparison requires numeric values") from ex

            asserter.assert_that(left_value).is_less_than(right_value)

    def _playback_string_assertion(self,
                                   left_value,
                                   right_value,
                                   operator: AssertionOperator,
                                   asserter):

        if operator == AssertionOperator.CONTAINS:
            asserter.assert_that(left_value).contains(right_value)

        elif operator == AssertionOperator.IN:
            try:
                collection = json.loads(right_value)

                if not isinstance(collection, list):
                    raise AssertionFailure(
                        "Expected a JSON list for 'is_in'")

                asserter.assert_that(left_value).is_in(collection)

            except json.JSONDecodeError as ex:
                raise AssertionFailure(
                    "Invalid JSON for 'is_in' operator") from ex

        elif operator == AssertionOperator.STARTS_WITH:
            asserter.assert_that(left_value).starts_with(right_value)

        elif operator == AssertionOperator.ENDS_WITH:
            asserter.assert_that(left_value).ends_with(right_value)

        elif operator == AssertionOperator.MATCHES_REGEX:
            asserter.assert_that(left_value).matches(right_value)

    def _playback_boolean_assertion(self,
                                    left_value,
                                    operator: AssertionOperator,
                                    asserter):
        left_value_boolean = self._parse_boolean(left_value)

        if operator == AssertionOperator.IS_TRUE:
            asserter.assert_that(left_value_boolean).is_true()

        elif operator == AssertionOperator.IS_FALSE:
            asserter.assert_that(left_value_boolean).is_false()

    def _playback_existence_assertion(self,
                                      left_value,
                                      operator: AssertionOperator,
                                      asserter):
        if operator == AssertionOperator.IS_NONE:
            asserter.assert_that(left_value).is_none()

        elif operator == AssertionOperator.IS_NOT_NONE:
            asserter.assert_that(left_value).is_not_none()

    def _playback_user_variable(self,
                                variable_name: str,
                                variable_value: str):
        self._context.set_variable(variable_name, variable_value)
        return PlaybackStepResult.success()

    def _parse_boolean(self, value: str) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in ("true", "1", "yes"):
                return True
            if normalized in ("false", "0", "no"):
                return False

        raise AssertionFailure(
            f"Boolean comparison requires boolean value, got '{value}'")

    def _perform_sendkeys(self, event):
        payload = event.get("payload", {})
        keys = payload.get("keys", [])
        target = payload.get("target", None)

        if target:
            # Nothing to do
            if not keys:
                print("NOT KEYS")
                return PlaybackStepResult.success()

            if keys[0].get("type") != "text":
                print("key combo not allowed with targetted")
                return PlaybackStepResult.fail("Special key combo not allowed")

            self._browser.playback_sendkeys(payload)
            return PlaybackStepResult.success()

        action_chains = ActionChains(self._browser.raw)

        for send_entry in keys:
            entry_type = send_entry.get("type")
            entry_value = send_entry.get("value")

            if entry_type == "text":
                action_chains.send_keys(entry_value)

            elif entry_type == "key":
                raw_modifiers = send_entry.get("modifiers")

                if raw_modifiers:
                    modifiers = raw_modifiers.split("+")

                    for modifier in modifiers:
                        action_chains.key_down(getattr(Keys, modifier))

                action_chains.send_keys(self._resolve_key(entry_value))

                if raw_modifiers:
                    modifiers = raw_modifiers.split("+")

                    for m in reversed(modifiers):
                        action_chains.key_up(getattr(Keys, m))

        action_chains.perform()

        return PlaybackStepResult.success()

    def _resolve_key(self, key: str):
        """Convert a recorded key name to a Selenium key."""

        if not key:
            return None

        # letters and digits
        if len(key) == 1:
            return key.lower()

        # special keys
        return getattr(Keys, key, key)
