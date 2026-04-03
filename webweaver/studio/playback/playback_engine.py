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
import json
from logging import Logger
import threading
from typing import Callable, Dict
import keyboard
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webweaver.studio.api_client import ApiClient
from webweaver.studio.browsing.studio_browser import (PlaybackStepResult,
                                                      StudioBrowser)
from webweaver.studio.persistence.recording_document import RestApiBodyType
from webweaver.studio.playback.playback_context import (PlaybackContext,
                                                        PlaybackVariableError)
from webweaver.studio.recording.recording import Recording
from webweaver.common.assertion import Assertions, AssertionFailure
from webweaver.common.assertion_operator import (AssertionOperator,
                                                 ASSERTION_NUMERICAL_OPERATORS,
                                                 ASSERTION_STRING_OPERATORS,
                                                 ASSERTION_BOOLEAN_OPERATORS,
                                                 ASSERTION_EXISTENCE_OPERATORS)


class PlaybackEngine:
    """
    Executes recorded playback events using a StudioBrowser.

    The PlaybackEngine is responsible for interpreting and executing a sequence
    of recorded events from a Recording. Each event is dispatched to a specific
    handler based on its type, allowing modular and extensible execution logic.

    The engine supports browser interactions, assertions, REST API calls,
    variable handling, and timing controls. All event execution is crash-safe:
    any unhandled exception is caught and converted into a failed
    PlaybackStepResult.

    Attributes:
        _browser (StudioBrowser): Browser abstraction used for executing DOM and navigation actions.
        _recording (Recording): The recording containing the list of events to execute.
        _logger (Logger): Logger instance scoped to the playback engine.
        _context (PlaybackContext): Runtime context for variable resolution and storage.
        _hard_assert (Assertions): Assertion handler for hard (failing) assertions.
        _soft_assert (Assertions): Assertion handler for soft (non-failing) assertions.
        _stop_event (threading.Event): Event used to signal playback interruption.
        _event_handlers_map (Dict[str, Callable[[dict], PlaybackStepResult]]):
            Mapping of event types to their corresponding handler functions.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 browser: StudioBrowser,
                 recording: Recording,
                 logger: Logger):
        """
        Initialize a new PlaybackEngine instance.

        Args:
            browser (StudioBrowser): The browser instance used for executing playback actions.
            recording (Recording): The recording containing events to be executed.
            logger (Logger): Base logger used for creating a scoped playback logger.
        """
        self._browser = browser
        self._recording = recording
        self._logger = logger.getChild(__name__)
        self._context = PlaybackContext(self._browser.raw)
        self._hard_assert: Assertions = Assertions(soft=False,
                                                   logger=self._logger)
        self._soft_assert: Assertions = Assertions(soft=True,
                                                   logger=self._logger)
        self._stop_event = threading.Event()

        self._event_handlers_map: Dict[
            str, Callable[[dict], PlaybackStepResult]] = {
            "assert": self._handle_assert,
            "dom.check": self._handle_dom_check,
            "dom.click": self._handle_dom_click,
            "dom.get": self._handle_dom_get,
            "dom.select": self._handle_dom_select,
            "dom.type": self._handle_dom_type,
            "nav.goto": self._handle_nav_goto,
            "rest_api": self._handle_rest_api,
            "scroll": self._handle_scroll,
            "sendkeys": self._handle_sendkeys,
            "user_variable": self._handle_user_variable,
            "wait": self._handle_wait,
        }

    @property
    def stop_event(self):
        """
        threading.Event: Event used to signal that playback should stop.

        This can be set externally to interrupt long-running operations such as waits.
        """
        return self._stop_event

    @property
    def context(self) -> PlaybackContext:
        return self._context

    def execute_event(self, event: dict):
        """
        Execute a single playback event.

        The event is dispatched to a handler based on its "type" field. If no handler
        is found, the event is treated as a no-op and considered successful.

        This method is crash-safe: any exception raised during execution is caught
        and returned as a failed PlaybackStepResult.

        Args:
            event (dict): The event to execute. Must contain a "type" key and
                optionally a "payload" dictionary.

        Returns:
            PlaybackStepResult: The result of executing the event.
        """
        try:
            event_type = event.get("type")
            payload = event.get("payload", {})

            handler = self._event_handlers_map.get(event_type)

            if handler is None:
                self._logger.debug("[PLAYBACK EVENT] Unknown event: %s",
                                   event_type)
                return PlaybackStepResult.success()

            return handler(payload)

        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.exception("Playback event crashed")
            return PlaybackStepResult.fail(str(e))

    #  --- Assertion Event ---

    def _handle_assert(self, payload):
        """
        Execute an assertion event.

        Resolves any template variables in the payload and performs the assertion
        using either a hard or soft assertion handler depending on configuration.

        Args:
            payload (dict): Assertion configuration including operator, values,
                and assertion type.

        Returns:
            PlaybackStepResult: Success if the assertion passes, otherwise failure.
        """
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
                f"Assert right variable '{right_value}' is not defined")

        operator_enum = AssertionOperator(operator)

        asserter = self._soft_assert if soft_assert else self._hard_assert

        try:
            # Process numerical assertion operators
            if operator_enum in ASSERTION_NUMERICAL_OPERATORS:
                self._assert_numerical_operator(left_value,
                                                right_value,
                                                operator_enum,
                                                asserter)

            if operator_enum in ASSERTION_STRING_OPERATORS:
                self._assert_string_assertion(left_value,
                                              right_value,
                                              operator_enum,
                                              asserter)

            if operator_enum in ASSERTION_BOOLEAN_OPERATORS:
                self._assert_boolean_assertion(left_value,
                                               operator_enum,
                                               asserter)

            if operator_enum in ASSERTION_EXISTENCE_OPERATORS:
                self._assert_existence_assertion(left_value,
                                                 operator_enum,
                                                 asserter)

        except AssertionFailure as ex:
            assert_msg: str = str(ex)
            return PlaybackStepResult.fail(assert_msg)

        return PlaybackStepResult.success()

    def _assert_numerical_operator(self,
                                   left_value,
                                   right_value,
                                   operator: AssertionOperator,
                                   asserter):
        """
        Perform a numerical comparison assertion.

        Args:
            left_value (Any): Left-hand operand.
            right_value (Any): Right-hand operand.
            operator (AssertionOperator): The comparison operator.
            asserter (Assertions): Assertion handler instance.

        Raises:
            AssertionFailure: If values are not numeric or assertion fails.
        """
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

    def _assert_string_assertion(self,
                                 left_value,
                                 right_value,
                                 operator: AssertionOperator,
                                 asserter):
        """
        Perform a string-based assertion.

        Args:
            left_value (str): Left-hand operand.
            right_value (str): Right-hand operand.
            operator (AssertionOperator): The string comparison operator.
            asserter (Assertions): Assertion handler instance.

        Raises:
            AssertionFailure: If assertion fails or input is invalid.
        """
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

    def _assert_boolean_assertion(self,
                                  left_value,
                                  operator: AssertionOperator,
                                  asserter):
        """
        Perform a boolean assertion.

        Args:
            left_value (Any): Value to evaluate as boolean.
            operator (AssertionOperator): Boolean operator.
            asserter (Assertions): Assertion handler instance.

        Raises:
            AssertionFailure: If value cannot be interpreted as boolean.
        """
        left_value_boolean = self._parse_boolean(left_value)

        if operator == AssertionOperator.IS_TRUE:
            asserter.assert_that(left_value_boolean).is_true()

        elif operator == AssertionOperator.IS_FALSE:
            asserter.assert_that(left_value_boolean).is_false()

    def _parse_boolean(self, value: str) -> bool:
        """
        Convert a value into a boolean.

        Supports common string representations such as "true", "false", "1", "0",
        "yes", and "no".

        Args:
            value (str): Value to convert.

        Returns:
            bool: Parsed boolean value.

        Raises:
            AssertionFailure: If the value cannot be interpreted as boolean.
        """
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

    def _assert_existence_assertion(self,
                                    left_value,
                                    operator: AssertionOperator,
                                    asserter):
        """
        Perform an existence check assertion.

        Args:
            left_value (Any): Value to check.
            operator (AssertionOperator): Existence operator.
            asserter (Assertions): Assertion handler instance.
        """
        if operator == AssertionOperator.IS_NONE:
            asserter.assert_that(left_value).is_none()

        elif operator == AssertionOperator.IS_NOT_NONE:
            asserter.assert_that(left_value).is_not_none()

    #  --- DOM element check ---
    def _handle_dom_check(self, payload):
        """
        Execute a DOM check event.

        Args:
            payload (dict): DOM check parameters.

        Returns:
            PlaybackStepResult: Result of the check operation.
        """
        return self._browser.playback_check(payload)

    #  --- DOM element Click ---
    def _handle_dom_click(self, payload):
        """
        Execute a DOM click event.

        Args:
            payload (dict): Click parameters.

        Returns:
            PlaybackStepResult: Result of the click action.
        """
        return self._browser.playback_click(payload)

    #  --- DOM element get ---
    def _handle_dom_get(self, payload):
        """
        Retrieve a DOM element or value.

        Args:
            payload (dict): Element query parameters.

        Returns:
            PlaybackStepResult: Result containing retrieved data.
        """
        self._logger.debug("[PLAYBACK EVENT] Element Get: %s", payload)
        return self._browser.playback_get(payload, self._context)

    #  --- DOM element select ---
    def _handle_dom_select(self, payload):
        """
        Execute a DOM select (dropdown) action.

        Args:
            payload (dict): Selection parameters including xpath and value.

        Returns:
            PlaybackStepResult: Result of the select action.
        """
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

    #  --- DOM element type ---
    def _handle_dom_type(self, payload):
        """
        Execute a DOM typing action.

        Args:
            payload (dict): Typing parameters including xpath and value.

        Returns:
            PlaybackStepResult: Result of the typing action.
        """
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

    #  --- DOM element type ---
    def _handle_nav_goto(self, payload):
        """
        Navigate the browser to a specified URL.

        Args:
            payload (dict): Must contain a "url" key.

        Returns:
            PlaybackStepResult: Success if navigation succeeds, otherwise failure.
        """
        url: str = payload.get("url")
        self._logger.debug("[PLAYBACK EVENT] Navigate to '%s'", url)

        try:
            self._browser.open_page(url)
        except WebDriverException:
            return PlaybackStepResult.fail(f"Unable to navigate to '{url}'")

        return PlaybackStepResult.success()

    #  --- REST API ---
    def _handle_rest_api(self, payload):
        """
        Execute a REST API call.

        Supports GET, POST, and DELETE operations. The result can optionally be
        stored in the playback context as a variable.

        Args:
            payload (dict): REST call configuration including URL, method,
                body, and output variable name.

        Returns:
            PlaybackStepResult: Result of the API call.
        """
        # pylint: disable=too-many-return-statements
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

    #  --- Page Scroll ---
    def _handle_scroll(self, payload):
        """
        Perform a scroll operation.

        Supports scrolling the page or a specific element to top, bottom,
        or a custom offset.

        Args:
            payload (dict): Scroll configuration.

        Returns:
            PlaybackStepResult: Result of the scroll operation.
        """
        scroll_type = payload.get("scroll_type")
        scroll_x = payload.get("x_scroll", 0)
        scroll_y = payload.get("y_scroll", 0)
        selector = payload.get("selector", "")

        element = None
        if selector:
            try:
                element = self._browser.raw.find_element(By.XPATH, selector)

            except WebDriverException:
                element = None

        # If we have a target element → ALWAYS scroll it directly
        if element:
            if scroll_type == "bottom":
                self._browser.raw.execute_script("""
                    arguments[0].scrollTop = arguments[0].scrollHeight;
                """, element)

            elif scroll_type == "top":
                self._browser.raw.execute_script("""
                    arguments[0].scrollTop = 0;
                """, element)

            elif scroll_type == "custom":
                self._browser.raw.execute_script("""
                    arguments[0].scrollTop += arguments[1];
                """, element, int(scroll_y))

            return PlaybackStepResult.success()

        # Only fallback if NO element found
        if scroll_type == "bottom":
            self._browser.scroll_to_bottom()

        elif scroll_type == "top":
            self._browser.scroll_to_top()

        elif scroll_type == "custom":
            self._browser.scroll_to(int(scroll_x), int(scroll_y))

        return PlaybackStepResult.success()

    #  --- Sendkeys ---

    def _handle_sendkeys(self, payload):
        """
        Execute a sendkeys event.

        Supports both raw keyboard input and Selenium-based input,
        including modifier combinations.

        Args:
            payload (dict): Key input configuration.

        Returns:
            PlaybackStepResult: Result of the sendkeys operation.
        """
        keys = payload.get("keys", [])
        target = payload.get("target", None)
        raw_mode = payload.get("raw_mode", False)

        if target:
            return self._perform_sendkeys_target(payload)

        action_chains = ActionChains(self._browser.raw)

        for send_entry in keys:
            entry_type = send_entry.get("type")

            if entry_type == "text":
                self._perform_sendkeys_text(send_entry, action_chains, raw_mode)

            elif entry_type == "key":
                if raw_mode:
                    self._perform_sendkeys_key_raw(send_entry)
                else:
                    self._perform_sendkeys_key_normal(send_entry, action_chains)

        if not raw_mode:
            action_chains.perform()

        return PlaybackStepResult.success()

    def _perform_sendkeys_target(self, payload):
        keys = payload.get("keys", [])

        # Nothing to do
        if not keys:
            return PlaybackStepResult.success()

        if keys[0].get("type") != "text":
            return PlaybackStepResult.fail("Special key combo not allowed")

        self._browser.playback_sendkeys(payload)
        return PlaybackStepResult.success()

    def _perform_sendkeys_text(self, key_entry, chain, raw_mode: bool):
        value = key_entry.get("value")

        if raw_mode:
            keyboard.write(value)

        else:
            chain.send_keys(value)

    def _perform_sendkeys_key_normal(self, key_entry, chain):
        raw_modifiers = key_entry.get("modifiers")
        entry_value = key_entry.get("value")

        if raw_modifiers:
            modifiers = raw_modifiers.split("+")

            for modifier in modifiers:
                chain.key_down(getattr(Keys, modifier))

        chain.send_keys(self._resolve_key(entry_value))

        if raw_modifiers:
            modifiers = raw_modifiers.split("+")

            for m in reversed(modifiers):
                chain.key_up(getattr(Keys, m))

    def _perform_sendkeys_key_raw(self, key_entry):
        raw_modifiers = key_entry.get("modifiers")
        entry_value = key_entry.get("value")

        if raw_modifiers:
            modifiers = raw_modifiers.lower().split("+")
            combo = "+".join(modifiers + [entry_value.lower()])
            keyboard.send(combo)
        else:
            keyboard.send(entry_value.lower())

    def _resolve_key(self, key: str):
        """Convert a recorded key name to a Selenium key."""

        if not key:
            return None

        # letters and digits
        if len(key) == 1:
            return key.lower()

        # special keys
        return getattr(Keys, key, key)

    #  --- User Variable ---
    def _handle_user_variable(self, payload):
        """
        Store a user-defined variable in the playback context.

        Args:
            payload (dict): Contains variable name and value.

        Returns:
            PlaybackStepResult: Always successful.
        """
        variable_name = payload.get("name")
        variable_value = payload.get("value")

        self._context.set_variable(variable_name, variable_value)
        return PlaybackStepResult.success()

    #  --- Wait ---
    def _handle_wait(self, payload):
        """
        Pause execution for a specified duration.

        The wait can be interrupted if the stop event is set.

        Args:
            payload (dict): Contains duration in milliseconds.

        Returns:
            PlaybackStepResult: Success if completed, failure if interrupted.
        """
        duration = payload.get("duration_ms")

        interrupted = self._stop_event.wait(duration / 1000)
        if interrupted:
            return PlaybackStepResult.fail("Playback stopped")

        return PlaybackStepResult.success()
