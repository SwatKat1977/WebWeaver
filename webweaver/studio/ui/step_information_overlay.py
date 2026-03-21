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


        '''
[EVENT] {'index': 4, 'timestamp': 4000, 'type': 'dom.check', 'payload': {'label': 'check checker is checked', 'xpath': '//checker', 'value': True, 'control_type': 'checkbox'}}
[EVENT] {'index': 7, 'timestamp': 7000, 'type': 'nav.goto', 'payload': {'label': '', 'url': 'https://www.google.com'}}
[EVENT] {'index': 8, 'timestamp': 8000, 'type': 'rest_api', 'payload': {'label': 'Perform REST API', 'base_url': 'url', 'call_type': 'get', 'rest_call': 'some_call', 'output_variable': '', 'body': None}
        '''

        step_type = step.get("type", "")
        payload = step.get("payload", {})

        if step["type"] == "assert":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"Operator Type :\n{payload['operator']}\n\n"
                f"Left Value: {payload['left_value']}\n"
                f"Right Value: {payload['right_value']}\n"
                f"Soft Assertion: {payload['soft_assert']}")

        elif step["type"] == "dom.check":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"XPath: {payload.get('xpath')}\n"
                f"Checked: {payload.get('value')}")

        elif step["type"] == "dom.click":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"XPath:\n{payload['xpath']}")

        elif step["type"] == "dom.get":
            output_var = payload.get("output_variable", "")

            body = (f"XPath: {payload['xpath']}\n"
                    f"Type: {payload['property_type']}\n")
            body += "" if not output_var else f"Output Variable: {output_var}"

            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(body)

        elif step["type"] == "dom.select":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"XPath: {payload['xpath']}\n"
                f"Value: {payload['value']}\n")

        elif step["type"] == "dom.type":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"XPath:\n{payload['xpath']}\n\n"
                f"Value:\n{payload['value']}")

        elif step["type"] == "nav.goto":
            self.title.SetLabel(f"Type: {step_type}")
            self.body.SetLabel(
                f"URL: {payload['url']}")

        elif step["type"] == "rest_api":
            self.title.SetLabel(f"Type: {step_type}")

            body = (f"Base Url: {payload.get('base_url', '')}\n"
                    f"Call Type: {payload.get('call_type', '')}\n"
                    f"Rest Call: {payload.get('rest_call', '')}\n")
            body += "" if not payload.get("body", "") else \
                f"Body:\n{payload.get('body')}"
            body += "" if not payload.get("output_variable", "") else \
                f"Output Variable: {payload.get('output_variable')}"
            self.body.SetLabel(body)

        elif step["type"] == "sendkeys":
            self.title.SetLabel(f"Type: {step_type}")

            body_text: str = ""

            if payload.get("target", ""):
                body_text += f"Target:\n{payload['xpath']}\n\n"

            keys_entry: str = "Entries:\n"
            keys = payload.get("keys", [])
            for entry in keys:
                keys_entry += (f"Type: {entry['type']}\n"
                               f"value {entry['value']}\n")

                keys_entry += "\n" if not entry["modifiers"] else \
                    f"Modifiers: {entry['modifiers']}"

            self.body.SetLabel(keys_entry)

        self.Layout()
        self.Fit()
