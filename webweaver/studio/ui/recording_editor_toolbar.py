import wx
from recording_toolbar_icons import (load_toolbar_edit_step_icon,
                                     load_toolbar_delete_step_icon,
                                     load_toolbar_move_step_up_icon,
                                     load_toolbar_move_step_down_icon)

TOOLBAR_ID_STEP_DELETE = wx.ID_HIGHEST + 6001


class RecordingEditorToolbar:
    def __init__(self, frame: wx.Frame, aui_mgr: wx.aui.AuiManager):
        self._frame = frame
        self._aui_mgr = aui_mgr

        self._toolbar = wx.aui.AuiToolBar(
            frame,
            style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_HORIZONTAL
        )

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_move_step_up_icon(),
            "Move Step Up")

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_move_step_down_icon(),
            "Move Step Down")

        self._toolbar.AddTool(
            wx.ID_ANY,
            "",
            load_toolbar_edit_step_icon(),
            "Edit Step")

        self._toolbar.AddTool(
            TOOLBAR_ID_STEP_DELETE,
            "",
            load_toolbar_delete_step_icon(),
            "Delete Step")

        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=TOOLBAR_ID_STEP_DELETE)

        self._toolbar.Realize()

        self._aui_mgr.AddPane(
            self._toolbar,
            wx.aui.AuiPaneInfo()
                .Name("StepsToolbar")
                .Caption("Steps")
                .ToolbarPane()
                .Top()
                .Row(2)
                .DockFixed(True)
                .Hide())

    @property
    def toolbar(self):
        return self._toolbar

    def _on_delete(self, _evt):
        wx.PostEvent(
            self._frame,
            wx.CommandEvent(wx.EVT_TOOL.typeId, TOOLBAR_ID_STEP_DELETE))
