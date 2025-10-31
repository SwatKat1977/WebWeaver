import wx

class Node:
    def __init__(self, id, name, pos):
        self.id = id
        self.name = name
        self.pos = wx.RealPoint(*pos)
        self.size = wx.Size(160, 100)
        self.inputs = ["In A"]
        self.outputs = ["Out A"]
        self.selected = False
        self.hovered = False

    def rect(self):
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)
