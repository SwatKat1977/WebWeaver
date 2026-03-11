import wx


class StepTree(wx.TreeCtrl):

    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.TR_DEFAULT_STYLE |
                  wx.TR_HAS_BUTTONS |
                  wx.TR_LINES_AT_ROOT |
                  wx.TR_FULL_ROW_HIGHLIGHT
        )

        self.drag_item = None

        self._create_images()

        self.root = self.AddRoot("Recording")

        self._build_demo_data()

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._on_end_drag)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)

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

    def add_step(self, parent, text, icon, step_data):

        item = self.AppendItem(parent, text)
        self.SetItemImage(item, icon)

        self.SetItemData(item, step_data)

        return item

    # ------------------------------------------------

    def _build_demo_data(self):

        login = self.AppendItem(self.root, "Login")
        self.SetItemBold(login)

        self.add_step(
            login,
            "Click login button",
            self.icon_play,
            {
                "type": "click",
                "xpath": "//button[@id=login]",
                "value": None})

        self.add_step(
            login,
            "Type username",
            self.icon_pass,
            {
                "type": "type",
                "xpath": "//input[@id=user]",
                "value": "username"})

        self.add_step(
            login,
            "Type password",
            self.icon_pass,
            {
                "type": "type",
                "xpath": "//input[@id=pass]",
                "value": "password"})

        payment = self.AppendItem(self.root, "Make Payment")
        self.SetItemBold(payment)

        self.add_step(
            payment,
            "Click pay button",
            self.icon_play,
            {
                "type": "click",
                "xpath": "//button[@id=pay]",
                "value": None})

        self.add_step(
            payment,
            "Assert payment value",
            self.icon_fail,
            {
                "type": "assert",
                "xpath": "//div[@id=payment]",
                "assert_type": "equals",
                "expected": "Success",
                "soft": True})

    # ------------------------------------------------

    def _on_begin_drag(self, evt):

        item = evt.GetItem()

        if item == self.root:
            return

        self.drag_item = item
        evt.Allow()

    # ------------------------------------------------

    def _on_end_drag(self, evt):

        if not self.drag_item:
            return

        pos = self.ScreenToClient(wx.GetMousePosition())
        target, flags = self.HitTest(pos)

        if not target.IsOk():
            self.drag_item = None
            return

        if target == self.drag_item:
            self.drag_item = None
            return

        if self._is_descendant(self.drag_item, target):
            self.drag_item = None
            return

        text = self.GetItemText(self.drag_item)
        icon = self.GetItemImage(self.drag_item)

        # save children
        children = []
        child, cookie = self.GetFirstChild(self.drag_item)

        while child.IsOk():
            children.append((self.GetItemText(child), self.GetItemImage(child)))
            child, cookie = self.GetNextChild(self.drag_item, cookie)

        self.Delete(self.drag_item)

        # -------------------------
        # DROP ON GROUP
        # -------------------------

        if self.ItemHasChildren(target) or target == self.root:

            parent = target
            new_item = self.AppendItem(parent, text)

        else:

            parent = self.GetItemParent(target)

            rect = self.GetBoundingRect(target)
            insert_after = pos.y > rect.y + rect.height / 2

            if insert_after:
                new_item = self.InsertItem(parent, target, text)
            else:
                prev = self.GetPrevSibling(target)

                if prev.IsOk():
                    new_item = self.InsertItem(parent, prev, text)
                else:
                    new_item = self.PrependItem(parent, text)

        if icon != -1:
            self.SetItemImage(new_item, icon)

        # restore children
        for t, i in children:
            c = self.AppendItem(new_item, t)
            if i != -1:
                self.SetItemImage(c, i)

        self.drag_item = None
        self.Expand(parent)

    # ------------------------------------------------

    def _is_descendant(self, parent, child):

        item = child

        while item.IsOk():

            if item == parent:
                return True

            item = self.GetItemParent(item)

        return False

    def _on_mouse_move(self, evt):

        pos = evt.GetPosition()

        item, flags = self.HitTest(pos)

        if not item.IsOk():
            self.SetToolTip(None)
            evt.Skip()
            return

        data = self.GetItemData(item)

        if not data:
            self.SetToolTip(None)
            evt.Skip()
            return

        tooltip = self._format_tooltip(data)

        self.SetToolTip(tooltip)

        evt.Skip()

    def _format_tooltip(self, step):

        if step["type"] == "click":

            return (
                "Action: Click\n"
                f"XPath: {step['xpath']}\n"
                f"Value: {step.get('value', '-')}"
            )

        if step["type"] == "type":

            return (
                "Action: Type\n"
                f"XPath: {step['xpath']}\n"
                f"Value: {step['value']}"
            )

        if step["type"] == "assert":

            return (
                "Action: Assert\n"
                f"XPath: {step['xpath']}\n"
                f"Type: {step['assert_type']}\n"
                f"Expected: {step['expected']}\n"
                f"Soft Assert: {step['soft']}"
            )

        return "Step"

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
