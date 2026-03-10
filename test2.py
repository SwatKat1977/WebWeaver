import wx


class StepTree(wx.TreeCtrl):

    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.TR_DEFAULT_STYLE |
                  wx.TR_HAS_BUTTONS |
                  wx.TR_LINES_AT_ROOT
        )

        self.drag_item = None

        self._create_images()

        self.root = self.AddRoot("Recording")

        self._build_demo_data()

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)

        self.ExpandAll()

    # ------------------------------------------------

    def _create_images(self):

        self.images = wx.ImageList(16, 16)

        self.icon_play = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, (16, 16))
        )

        self.icon_pass = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16, 16))
        )

        self.icon_fail = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, (16, 16))
        )

        self.AssignImageList(self.images)

    # ------------------------------------------------

    def add_step(self, parent, text, icon):

        item = self.AppendItem(parent, text)
        self.SetItemImage(item, icon)

        return item

    # ------------------------------------------------

    def _build_demo_data(self):

        login = self.AppendItem(self.root, "Login")
        self.SetItemBold(login)

        self.add_step(login, "Click login button", self.icon_play)
        self.add_step(login, "Type username", self.icon_pass)
        self.add_step(login, "Type password", self.icon_pass)

        payment = self.AppendItem(self.root, "Make Payment")
        self.SetItemBold(payment)

        self.add_step(payment, "Click pay button", self.icon_play)
        self.add_step(payment, "Assert payment value", self.icon_fail)

    # ------------------------------------------------

    def on_begin_drag(self, evt):
        item = evt.GetItem()

        if item == self.root:
            return  # root cannot be dragged

        self.drag_item = item
        evt.Allow()

    # ------------------------------------------------

    def on_end_drag(self, evt):

        if not self.drag_item:
            return

        target = evt.GetItem()

        if not target.IsOk():
            return

        # If dropping onto a step, move to its parent group
        if target != self.root and not self.ItemHasChildren(target):
            target = self.GetItemParent(target)

        if target == self.drag_item:
            return

        new_item = self.AppendItem(
            target,
            self.GetItemText(self.drag_item)
        )

        # copy icon
        icon = self.GetItemImage(self.drag_item)
        if icon != -1:
            self.SetItemImage(new_item, icon)

        self.copy_children(self.drag_item, new_item)

        self.Delete(self.drag_item)

        self.drag_item = None

        self.Expand(target)

    # ------------------------------------------------

    def copy_children(self, src, dst):

        child, cookie = self.GetFirstChild(src)

        while child.IsOk():

            new_child = self.AppendItem(dst, self.GetItemText(child))

            icon = self.GetItemImage(child)
            if icon != -1:
                self.SetItemImage(new_child, icon)

            self.copy_children(child, new_child)

            child, cookie = self.GetNextChild(src, cookie)


# ------------------------------------------------


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None,
            title="Step Editor Demo",
            size=(600, 400)
        )

        panel = wx.Panel(self)

        tree = StepTree(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tree, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)


# ------------------------------------------------


class App(wx.App):

    def OnInit(self):

        frame = MainFrame()
        frame.Show()

        return True


# ------------------------------------------------


if __name__ == "__main__":
    app = App()
    app.MainLoop()
