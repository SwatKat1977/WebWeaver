
import wx

class InspectorPanel(wx.Panel):
    def __init__(self, parent: wx.Window):
        """
        Construct a new SolutionExplorerPanel.

        Parameters
        ----------
        parent : wx.Window
            Parent window that owns this panel.
        """
        super().__init__(parent)

        # Vertical layout: buttons at top, log below
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # --- Log area (multiline text) ---
        self._log: wx.TextCtrl = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        main_sizer.Add(self._log,
                       1,
                       wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       5)

        self.SetSizer(main_sizer)
