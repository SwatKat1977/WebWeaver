import wx
import wx.propgrid as wxpg
import math, json, os
from node_editor_frame import NodeEditorFrame




if __name__ == "__main__":
    app = wx.App(False)
    NodeEditorFrame()
    app.MainLoop()
