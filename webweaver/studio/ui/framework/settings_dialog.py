import typing
import wx
from webweaver.studio.ui.framework.page_definition import PageDefinition
from webweaver.studio.ui.framework.settings_page import SettingsPage

class SettingsDialog(wx.Dialog):
    def __init__(self,
                 parent, context,
                 page_definitions: typing.List[PageDefinition]):
        super().__init__(parent)

        self.tree = wx.TreeCtrl(self)
        self.content_area = wx.Panel(self)

        self.pages: dict[wx.TreeItemId, SettingsPage] = {}
