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
import wx


class StepInformationOverlay(wx.PopupTransientWindow):
    """Popup overlay displaying information about a playback step.

    This transient window presents contextual details for a given step in the
    playback timeline, such as click, type, or assert actions. It is designed
    to appear as a lightweight informational tooltip-style overlay.

    Attributes:
        title (wx.StaticText): Label displaying the step type.
        body (wx.StaticText): Label displaying detailed step information.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent):
        """Initializes the StepInformationOverlay.

        Args:
            parent (wx.Window): The parent window for this popup.
        """
        super().__init__(parent)

        panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        panel.SetBackgroundColour(wx.Colour(255, 255, 240))

        self.title = wx.StaticText(panel, label="")
        self.title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                   wx.FONTSTYLE_NORMAL,
                                   wx.FONTWEIGHT_BOLD))

        self.body = wx.StaticText(panel, label="")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.title, 0, wx.ALL, 8)
        sizer.Add(self.body, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(sizer)

        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(panel)

        self.SetSizerAndFit(main)

    def update(self, step):
        """Updates the overlay content based on the provided step.

        The displayed title and body content are adjusted depending on the
        step type. Supported step types include "click", "type", and "assert".

        Args:
            step (dict): A dictionary describing the step. Expected keys vary
                by type but may include:
                    - type (str): The step type ("click", "type", "assert").
                    - xpath (str): XPath of the target element.
                    - value (str, optional): Input value for click/type steps.
                    - assert_type (str, optional): Assertion type.
                    - expected (str, optional): Expected value for assertions.
                    - soft (bool, optional): Whether assertion is soft.

        Raises:
            KeyError: If required keys for a given step type are missing.
        """

        step_type = step.get("type", "")
        payload = step.get("payload", {})

        self.title.SetLabel(f"Type: {step_type}")

        handlers = {
            "assert": self._render_assert,
            "dom.check": self._render_dom_check,
            "dom.click": self._render_dom_click,
            "dom.get": self._render_dom_get,
            "dom.select": self._render_dom_select,
            "dom.type": self._render_dom_type,
            "nav.goto": self._render_nav_goto,
            "rest_api": self._render_rest_api,
            "scroll": self._render_scroll,
            "sendkeys": self._render_sendkeys,
            "user_variable": self._render_user_variable,
            "wait": self._render_wait,
        }

        handler = handlers.get(step_type)

        if handler:
            body = handler(payload)
        else:
            body = "Unknown step type"

        self.body.SetLabel(body)

        self.Layout()
        self.Fit()

    def _render_assert(self, payload: dict):
        return (f"Operator Type :\n{payload['operator']}\n\n"
                f"Left Value: {payload['left_value']}\n"
                f"Right Value: {payload['right_value']}\n"
                f"Soft Assertion: {payload['soft_assert']}")

    def _render_dom_check(self, payload: dict):
        return (f"XPath: {payload.get('xpath')}\n"
                f"Checked: {payload.get('value')}")

    def _render_dom_click(self, payload: dict):
        return f"XPath:\n{payload['xpath']}"

    def _render_dom_get(self, payload: dict):
        output_var = payload.get("output_variable", "")
        body = (f"XPath: {payload['xpath']}\n"
                f"Type: {payload['property_type']}\n")
        body += "" if not output_var else f"Output Variable: {output_var}"
        return body

    def _render_dom_select(self, payload: dict):
        return (f"XPath: {payload['xpath']}\n"
                f"Value: {payload['value']}\n")

    def _render_dom_type(self, payload: dict):
        return (f"XPath:\n{payload['xpath']}\n\n"
                f"Value:\n{payload['value']}")

    def _render_nav_goto(self, payload: dict):
        return f"URL: {payload['url']}"

    def _render_rest_api(self, payload: dict):
        body = (f"Base Url: {payload.get('base_url', '')}\n"
                f"Call Type: {payload.get('call_type', '')}\n"
                f"Rest Call: {payload.get('rest_call', '')}\n")
        body += "" if not payload.get("body", "") else \
            f"Body:\n{payload.get('body')}"
        body += "" if not payload.get("output_variable", "") else \
            f"Output Variable: {payload.get('output_variable')}"
        return body

    def _render_scroll(self, payload: dict):
        return (f"Scroll Type: {payload.get('scroll_type')}\n"
                f"x: {payload.get('x_scroll', '-')} | "
                f"y: {payload.get('y_scroll', '-')}")

    def _render_sendkeys(self, payload: dict):
        body_text: str = ""

        if payload.get("target", ""):
            body_text += f"Target:\n{payload['target']}\n"

        keys = payload.get("keys", [])
        if keys:
            body_text += "Entries:\n"
            for entry in keys:
                body_text += "\n"
                body_text += (f"Type: {entry['type']}\n"
                              f"value {entry['value']}\n")
                body_text += "" if not entry.get("modifiers", "") else \
                    f"Modifiers: {entry['modifiers']}"

        return body_text

    def _render_user_variable(self, payload: dict):
        return (f"Variable Name: {payload.get('name', '')}\n"
                f"Value: {payload.get('value', '')}")

    def _render_wait(self, payload: dict):
        return f"Duration: {payload.get('duration_ms', '')} ms\n"
