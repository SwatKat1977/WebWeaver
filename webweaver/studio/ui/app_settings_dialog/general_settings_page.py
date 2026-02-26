import wx
from webweaver.studio.ui.framework.settings_page import SettingsPage
from webweaver.studio.studio_app_settings import StudioAppSettings


class GeneralSettingsPage(SettingsPage):
    """
    Settings page for general application behaviour.
    """

    def __init__(self, parent, context: StudioAppSettings):
        super().__init__(parent)

        self._settings = context

        outer = wx.BoxSizer(wx.VERTICAL)

        # ---- Content container ----
        content = wx.BoxSizer(wx.VERTICAL)

        # Section Title
        title = wx.StaticText(self, label="General")
        font = title.GetFont()
        font.MakeBold()
        font.SetPointSize(font.GetPointSize() + 1)
        title.SetFont(font)
        content.Add(title, 0, wx.BOTTOM, 10)

        # Divider
        content.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.BOTTOM, 20)

        # ---- Startup behaviour section ----
        self._start_max_checkbox = wx.CheckBox(
            self,
            label="Start maximised")
        content.Add(self._start_max_checkbox, 0, wx.BOTTOM, 10)

        # Section Title
        title = wx.StaticText(self, label="Startup")
        font = title.GetFont()
        font.MakeBold()
        font.SetPointSize(font.GetPointSize() + 1)
        title.SetFont(font)
        content.Add(title, 0, wx.BOTTOM, 10)

        # Divider
        content.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.BOTTOM, 20)

        # ---- Startup behaviour section ----
        self._restore_last_opened_solution_checkbox = wx.CheckBox(
            self,
            label="Restore last opened solution")
        content.Add(self._restore_last_opened_solution_checkbox,
                    0,
                    wx.BOTTOM,
                    10)
        self._restore_last_opened_solution_checkbox.Enable(False)

        outer.Add(content, 0, wx.ALL | wx.EXPAND, 20)
        outer.AddStretchSpacer()

        self.SetSizer(outer)

    # -------------------------
    # SettingsPage overrides
    # -------------------------

    def load(self):
        self._start_max_checkbox.SetValue(
            self._settings.start_maximised
        )

    def validate(self):
        # No validation needed for checkboxes
        return super().validate()

    def apply(self):
        self._settings.start_maximised = \
            self._start_max_checkbox.GetValue()
