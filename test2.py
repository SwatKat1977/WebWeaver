from enum import Enum
import wx


class StepStatus(Enum):
    NOT_RUN = 0
    RUNNING = 1
    PASSED = 2
    FAILED = 3
    WARNING = 4


class StepInspector(wx.PopupTransientWindow):

    def __init__(self, parent):
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

        if step["type"] == "click":
            self.title.SetLabel("Click")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Value:\n{step.get('value','-')}")

        elif step["type"] == "type":
            self.title.SetLabel("Type")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Value:\n{step['value']}")

        elif step["type"] == "assert":
            self.title.SetLabel("Assert")
            self.body.SetLabel(
                f"XPath:\n{step['xpath']}\n\n"
                f"Type: {step['assert_type']}\n"
                f"Expected: {step['expected']}\n"
                f"Soft: {step['soft']}")

        self.Layout()
        self.Fit()


class StepTree(wx.TreeCtrl):

    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.TR_DEFAULT_STYLE |
                  wx.TR_HAS_BUTTONS |
                  wx.TR_LINES_AT_ROOT |
                  wx.TR_FULL_ROW_HIGHLIGHT)

        self.drag_item = None
        self.inspector = StepInspector(self)
        self.hover_item = None
        self.hover_timer = wx.Timer(self)
        self.pending_hover_item = None
        self.drop_indicator_y = None

        self._create_images()

        self.root = self.AddRoot("Recording")

        self._build_demo_data()

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._on_end_drag)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_mouse_leave)
        self.Bind(wx.EVT_TIMER, self._on_hover_timer, self.hover_timer)
        self.Bind(wx.EVT_PAINT, self._on_paint)

        self.ExpandAll()

    def _create_images(self):

        self.images = wx.ImageList(16, 16)

        self._icon_not_run = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16, 16)))

        self._icon_running = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_OTHER, (16, 16)))

        self._icon_pass = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, (16, 16)))

        self._icon_fail = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, (16, 16)))

        self._icon_warning = self.images.Add(
            wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_OTHER, (16, 16)))

        self.AssignImageList(self.images)

        self._status_icons = {
            StepStatus.NOT_RUN: self._icon_not_run,
            StepStatus.RUNNING: self._icon_running,
            StepStatus.PASSED: self._icon_pass,
            StepStatus.FAILED: self._icon_fail,
            StepStatus.WARNING: self._icon_warning
        }

    def add_step(self, parent, text, icon, step_data):

        item = self.AppendItem(parent, text)
        self.SetItemImage(item, icon)

        self.SetItemData(item, step_data)

        return item

    def set_step_status(self, item, status: StepStatus):

        if not item or not item.IsOk():
            return

        icon = self._status_icons.get(status, -1)

        if icon == -1:
            self.SetItemImage(item, -1)
        else:
            self.SetItemImage(item, icon)

    def reset_statuses(self):

        def walk(parent):

            child, cookie = self.GetFirstChild(parent)

            while child.IsOk():

                if self.GetItemData(child):  # step node
                    self.SetItemImage(child, self._status_icons[StepStatus.NOT_RUN])

                walk(child)

                child, cookie = self.GetNextChild(parent, cookie)

        walk(self.root)

    def _build_demo_data(self):

        login = self.AppendItem(self.root, "Login")
        self.SetItemBold(login)

        self.add_step(
            login,
            "Click login button",
            self._icon_running,
            {
                "type": "click",
                "xpath": "//button[@id=login]",
                "value": None})

        self.add_step(
            login,
            "Type username",
            self._icon_warning,
            {
                "type": "type",
                "xpath": "//input[@id=user]",
                "value": "username"})

        self.add_step(
            login,
            "Type password",
            self._icon_warning,
            {
                "type": "type",
                "xpath": "//input[@id=pass]",
                "value": "password"})

        payment = self.AppendItem(self.root, "Make Payment")
        self.SetItemBold(payment)

        self.add_step(
            payment,
            "Click pay button",
            self._icon_fail,
            {
                "type": "click",
                "xpath": "//button[@id=pay]",
                "value": None})

        self.add_step(
            payment,
            "Assert payment value",
            self._icon_fail,
            {
                "type": "assert",
                "xpath": "//div[@id=payment]",
                "assert_type": "equals",
                "expected": "Success",
                "soft": True})

    def _on_begin_drag(self, evt):

        item = evt.GetItem()

        if item == self.root:
            return

        self.drag_item = item
        evt.Allow()

    def _on_end_drag(self, _evt):

        self._clear_drop_indicator()

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
        data = self.GetItemData(self.drag_item)
        bold = self.IsBold(self.drag_item)
        expanded = self.IsExpanded(self.drag_item)

        # save children
        children = []
        child, cookie = self.GetFirstChild(self.drag_item)

        while child.IsOk():
            children.append((
                self.GetItemText(child),
                self.GetItemImage(child),
                self.GetItemData(child),
                self.IsBold(child)
            ))
            child, cookie = self.GetNextChild(self.drag_item, cookie)

        self.Delete(self.drag_item)

        # -------------------------
        # DROP ON GROUP
        # -------------------------
        if not self.GetItemData(target) or target == self.root:
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

        self.SetItemData(new_item, data)

        if bold:
            self.SetItemBold(new_item)

        # restore children
        for t, i, d, b in children:
            c = self.AppendItem(new_item, t)

            if i != -1:
                self.SetItemImage(c, i)

            self.SetItemData(c, d)

            if b:
                self.SetItemBold(c)

        self.drag_item = None
        self.Expand(parent)

        # ensure moved groups stay expanded
        if expanded:
            self.Expand(new_item)

    def _is_descendant(self, parent, child):

        item = child

        while item.IsOk():

            if item == parent:
                return True

            item = self.GetItemParent(item)

        return False

    def _on_mouse_move(self, evt):

        if self.drag_item:
            pos = evt.GetPosition()
            item, flags = self.HitTest(pos)

            if item.IsOk():
                rect = self.GetBoundingRect(item)
                self.drop_indicator_y = rect.y + rect.height // 2
                self.Refresh()

        pos = evt.GetPosition()

        item, flags = self.HitTest(pos)

        if not item.IsOk():
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self.inspector.Hide()
            self.hover_item = None
            self.UnselectAll()
            evt.Skip()
            return

        data = self.GetItemData(item)

        # group node, not a real step
        if not data:
            self.hover_timer.Stop()
            self.pending_hover_item = None
            self.inspector.Hide()
            self.hover_item = None
            self.UnselectAll()
            evt.Skip()
            return

        # already showing this item
        if item == self.hover_item:
            evt.Skip()
            return

        # remember candidate hover item and restart timer
        self.pending_hover_item = item
        self.hover_timer.StartOnce(75)

        evt.Skip()

    def _on_mouse_leave(self, evt):
        self.hover_timer.Stop()
        self.pending_hover_item = None
        self.inspector.Hide()
        self.hover_item = None
        self.UnselectAll()

        evt.Skip()

    def _on_hover_timer(self, _evt):
        item = self.pending_hover_item

        if not item or not item.IsOk():
            return

        data = self.GetItemData(item)

        if not data:
            return

        self.hover_item = item
        self.SelectItem(item)

        self.inspector.update(data)

        pos = self.ScreenToClient(wx.GetMousePosition())
        screen_pos = self.ClientToScreen(pos)
        screen_pos.y += 20

        self.inspector.Position(screen_pos, (0, 0))
        self.inspector.Popup()

    def _on_paint(self, evt):

        evt.Skip()

        if self.drop_indicator_y is None:
            return

        wx.CallAfter(self._draw_drop_indicator)

    def _draw_drop_indicator(self):

        if self.drop_indicator_y is None:
            return

        dc = wx.ClientDC(self)

        dc.SetPen(wx.Pen(wx.Colour(0, 120, 215), 2))

        width, _ = self.GetClientSize()

        dc.DrawLine(0, self.drop_indicator_y, width, self.drop_indicator_y)

    def _clear_drop_indicator(self):
        if self.drop_indicator_y is not None:
            self.drop_indicator_y = None
            self.Refresh()

# ------------------------------------------------


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None,
            title="Step Editor Demo",
            size=(600, 400))

        panel = wx.Panel(self)

        tree = StepTree(panel)

        tree.reset_statuses()

        """
        tree.set_step_status(step1, StepStatus.RUNNING)
        tree.set_step_status(step1, StepStatus.PASSED)

        tree.set_step_status(step2, StepStatus.RUNNING)
        tree.set_step_status(step2, StepStatus.FAILED)
        """

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
