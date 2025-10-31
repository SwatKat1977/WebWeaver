import wx
import wx.propgrid as wxpg
import math, json, os

CONFIG_PATH = os.path.expanduser("~/.weaver_settings.json")

# ---------------- Settings ----------------

def load_settings():
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return {
                "snap_enabled": bool(data.get("snap_enabled", False)),
                "snap_size": int(data.get("snap_size", 20)),
            }
    except Exception:
        return {"snap_enabled": False, "snap_size": 20}

def save_settings(data):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as ex:
        wx.LogError(f"Could not save settings: {ex}")

# ---------------- Model ----------------

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

class Connection:
    def __init__(self, out_node, out_index, in_node, in_index):
        self.out_node = out_node
        self.out_index = out_index
        self.in_node = in_node
        self.in_index = in_index
        self.hovered = False

# ---------------- Canvas ----------------

class NodeCanvas(wx.Panel):
    next_id = 100

    def __init__(self, parent, on_node_selected, settings):
        # wx.WANTS_CHARS helps ensure we can receive focus/keys when needed
        super().__init__(parent, style=wx.WANTS_CHARS)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.on_node_selected = on_node_selected
        self.settings = settings

        self.nodes = [
            Node(1, "Start", (80, 80)),
            Node(2, "Condition", (360, 160)),
            Node(3, "End", (700, 120)),
        ]
        self.connections = []

        # Camera
        self.scale = 1.0
        self.offset = wx.RealPoint(0, 0)

        # Mouse state
        self.last_mouse = wx.Point(0, 0)
        self.drag_node = None
        self.dragging = False
        self.dragging_connection = False
        self.start_pin = None  # (node, out_index, "out")

        # Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    # ----- Helpers -----

    def screen_to_world(self, pt: wx.Point) -> wx.RealPoint:
        return wx.RealPoint(
            (pt.x - self.offset.x) / self.scale,
            (pt.y - self.offset.y) / self.scale
        )

    def snap_val(self, v: float) -> float:
        s = max(1, int(self.settings["snap_size"]))
        return round(v / s) * s

    # ----- Paint -----

    def OnPaint(self, _):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        gc.SetBrush(wx.Brush(wx.Colour(28, 29, 33)))
        gc.DrawRectangle(0, 0, w, h)

        gc.Translate(self.offset.x, self.offset.y)
        gc.Scale(self.scale, self.scale)

        self.draw_grid(gc)
        self.draw_connections(gc)
        self.draw_nodes(gc)
        self.draw_temp_connection(gc)

    def draw_grid(self, gc):
        w, h = self.GetClientSize()
        step = 40
        tl = self.screen_to_world(wx.Point(0, 0))
        br = self.screen_to_world(wx.Point(w, h))
        start_x = math.floor(tl.x / step) * step
        end_x   = math.ceil(br.x / step) * step
        start_y = math.floor(tl.y / step) * step
        end_y   = math.ceil(br.y / step) * step

        fine = wx.Pen(wx.Colour(45, 46, 50))
        bold = wx.Pen(wx.Colour(60, 61, 65))

        i, x = 0, start_x
        while x <= end_x:
            gc.SetPen(bold if i % 5 == 0 else fine)
            gc.StrokeLine(x, start_y, x, end_y)
            x += step; i += 1

        j, y = 0, start_y
        while y <= end_y:
            gc.SetPen(bold if j % 5 == 0 else fine)
            gc.StrokeLine(start_x, y, end_x, y)
            y += step; j += 1

    def draw_nodes(self, gc):
        for n in self.nodes:
            r = n.rect()

            # shadow
            gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 130)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawRoundedRectangle(r.x + 6, r.y + 6, r.width, r.height, 10)

            # selection glow
            if n.selected:
                gc.SetBrush(wx.Brush(wx.Colour(255, 140, 0, 80)))
                gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
                gc.DrawRoundedRectangle(r.x - 4, r.y - 4, r.width + 8, r.height + 8, 12)

            # body
            fill = wx.Colour(45, 47, 52)
            border = wx.Colour(255, 140, 0) if n.selected else wx.Colour(60, 62, 68)
            gc.SetBrush(wx.Brush(fill))
            gc.SetPen(wx.Pen(border, 2))
            gc.DrawRoundedRectangle(r.x, r.y, r.width, r.height, 10)

            # title
            gc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                       wx.Colour(255, 255, 255))
            gc.DrawText(n.name, r.x + 10, r.y + 8)

            self.draw_pins(gc, n)

    def draw_pins(self, gc, n: Node):
        pr = 5
        spacing = 20
        text_offset = 22

        # Inputs (orange, left)
        for i, label in enumerate(n.inputs):
            px = n.pos.x - 10
            py = n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(255, 100, 60)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            gc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                       wx.Colour(255, 255, 255))
            gc.DrawText(label, px + text_offset - 10, py - 7)

        # Outputs (green, right)
        for i, label in enumerate(n.outputs):
            px = n.pos.x + n.size.width + 10
            py = n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            text_w, _, _, _ = gc.GetFullTextExtent(label)
            gc.DrawText(label, px - text_w - text_offset + 10, py - 7)

    def draw_connections(self, gc):
        for c in self.connections:
            n1, n2 = c.out_node, c.in_node
            p1 = wx.RealPoint(n1.pos.x + n1.size.width + 10, n1.pos.y + 30 + c.out_index * 20)
            p2 = wx.RealPoint(n2.pos.x - 10, n2.pos.y + 30 + c.in_index * 20)
            d = abs(p2.x - p1.x) * 0.5
            colour = wx.Colour(255, 255, 255) if c.hovered else wx.Colour(160, 160, 160)
            gc.SetPen(wx.Pen(colour, 2))
            path = gc.CreatePath()
            path.MoveToPoint(p1.x, p1.y)
            path.AddCurveToPoint(p1.x + d, p1.y, p2.x - d, p2.y, p2.x, p2.y)
            gc.StrokePath(path)

    def draw_temp_connection(self, gc):
        if not (self.dragging_connection and self.start_pin):
            return
        node, idx, _ = self.start_pin
        start = wx.RealPoint(node.pos.x + node.size.width + 10, node.pos.y + 30 + idx * 20)
        end = self.screen_to_world(self.last_mouse)
        gc.SetPen(wx.Pen(wx.Colour(220, 200, 100), 2, wx.PENSTYLE_DOT))
        d = abs(end.x - start.x) * 0.5
        path = gc.CreatePath()
        path.MoveToPoint(start.x, start.y)
        path.AddCurveToPoint(start.x + d, start.y, end.x - d, end.y, end.x, end.y)
        gc.StrokePath(path)

    # ----- Interaction -----

    def OnLeftDown(self, event):
        self.CaptureMouse()
        self.last_mouse = event.GetPosition()
        world = self.screen_to_world(self.last_mouse)

        # Start connection drag? (from an OUTPUT pin)
        for n in reversed(self.nodes):
            for i, _ in enumerate(n.outputs):
                px = n.pos.x + n.size.width + 10
                py = n.pos.y + 30 + i * 20
                if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
                    self.dragging_connection = True
                    self.start_pin = (n, i, "out")
                    self.SetFocus()  # keep focus for keys while dragging
                    self.Refresh(False)
                    return

        # Node selection with explicit numeric bounds (robust)
        clicked = None
        for n in reversed(self.nodes):
            r = n.rect()
            if (r.x <= world.x <= r.x + r.width) and (r.y <= world.y <= r.y + r.height):
                clicked = n
                break

        for n in self.nodes:
            n.selected = (n == clicked)
        self.on_node_selected(clicked)

        self.drag_node = clicked
        self.dragging = True
        self.SetFocus()
        self.Refresh(False)

    def OnLeftUp(self, event):
        if self.HasCapture():
            self.ReleaseMouse()

        # Complete connection if dragging
        if self.dragging_connection and self.start_pin:
            world = self.screen_to_world(event.GetPosition())
            for n in self.nodes:
                for i, _ in enumerate(n.inputs):
                    px = n.pos.x - 10
                    py = n.pos.y + 30 + i * 20
                    if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
                        s_node, s_idx, _ = self.start_pin
                        self.connections.append(Connection(s_node, s_idx, n, i))
                        break

        self.dragging = False
        self.drag_node = None
        self.dragging_connection = False
        self.start_pin = None
        self.Refresh(False)

    def OnMouseMove(self, event):
        world = self.screen_to_world(event.GetPosition())

        # Hover highlight for connections
        for c in self.connections:
            n1, n2 = c.out_node, c.in_node
            p1 = wx.RealPoint(n1.pos.x + n1.size.width + 10, n1.pos.y + 30 + c.out_index * 20)
            p2 = wx.RealPoint(n2.pos.x - 10, n2.pos.y + 30 + c.in_index * 20)
            c.hovered = self.point_near_curve(world, p1, p2, tol=6)

        if event.Dragging() and event.LeftIsDown():
            if self.dragging_connection:
                self.last_mouse = event.GetPosition()
            elif self.drag_node:
                delta = self.screen_to_world(event.GetPosition()) - self.screen_to_world(self.last_mouse)
                self.drag_node.pos.x += delta.x
                self.drag_node.pos.y += delta.y
                if self.settings["snap_enabled"]:
                    self.drag_node.pos.x = self.snap_val(self.drag_node.pos.x)
                    self.drag_node.pos.y = self.snap_val(self.drag_node.pos.y)
                self.last_mouse = event.GetPosition()
            else:
                # Pan empty space
                delta = event.GetPosition() - self.last_mouse
                self.offset.x += delta.x
                self.offset.y += delta.y
                self.last_mouse = event.GetPosition()
        else:
            self.last_mouse = event.GetPosition()

        self.Refresh(False)

    def OnMouseWheel(self, event):
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        zoom = 1.1 if delta > 0 else 0.9
        mouse = event.GetPosition()
        before = self.screen_to_world(mouse)
        self.scale = max(0.3, min(2.5, self.scale * zoom))
        after = self.screen_to_world(mouse)
        self.offset.x += (after.x - before.x) * self.scale
        self.offset.y += (after.y - before.y) * self.scale
        self.Refresh(False)

    def OnContextMenu(self, event):
        world = self.screen_to_world(event.GetPosition())
        hovered_conn = next((c for c in self.connections if c.hovered), None)

        menu = wx.Menu()
        if hovered_conn:
            del_item = menu.Append(wx.ID_DELETE, "Delete Connection")
            self.Bind(wx.EVT_MENU, lambda evt, c=hovered_conn: self.delete_connection(c), del_item)
        else:
            add_item = menu.Append(-1, "Add Node Here")
            self.Bind(wx.EVT_MENU, lambda evt, pos=world: self.add_node("Node", pos), add_item)
            menu.AppendSeparator()
            pref_item = menu.Append(-1, "Preferences…")
            self.Bind(wx.EVT_MENU, lambda evt: self.GetParent().GetParent().open_preferences(), pref_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def OnMouseLeave(self, _):
        for c in self.connections:
            c.hovered = False
        self.Refresh(False)

    # ----- Geometry helpers -----

    def point_near_curve(self, pt, p1, p2, tol=6):
        steps = 24
        mind = 1e9
        d = abs(p2.x - p1.x) * 0.5
        for s in [i / steps for i in range(steps + 1)]:
            bx = ((1 - s)**3) * p1.x + 3 * ((1 - s)**2) * s * (p1.x + d) + \
                 3 * (1 - s) * (s**2) * (p2.x - d) + (s**3) * p2.x
            by = ((1 - s)**3) * p1.y + 3 * ((1 - s)**2) * s * p1.y + \
                 3 * (1 - s) * (s**2) * p2.y + (s**3) * p2.y
            mind = min(mind, math.hypot(pt.x - bx, pt.y - by))
        return mind <= tol

    def delete_connection(self, c):
        if c in self.connections:
            self.connections.remove(c)
            self.Refresh(False)

    def add_node(self, name, pos):
        n = Node(NodeCanvas.next_id, name, (pos.x, pos.y))
        NodeCanvas.next_id += 1
        self.nodes.append(n)
        self.Refresh(False)

# ---------------- Preferences Dialog ----------------

class PreferencesDialog(wx.Dialog):
    def __init__(self, parent, settings):
        super().__init__(parent, title="Preferences", size=(320, 180))
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.chk_snap = wx.CheckBox(pnl, label="Enable Grid Snapping")
        self.chk_snap.SetValue(settings["snap_enabled"])

        grid = wx.FlexGridSizer(1, 2, 8, 8)
        grid.Add(wx.StaticText(pnl, label="Snap Size (px):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_snap = wx.SpinCtrl(pnl, min=5, max=200, initial=settings["snap_size"])
        grid.Add(self.spin_snap, 1, wx.EXPAND)

        vbox.Add(self.chk_snap, 0, wx.ALL, 10)
        vbox.Add(grid, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 8)
        pnl.SetSizer(vbox)

# ---------------- Frame ----------------

class NodeEditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Node Editor", size=(1200, 720))
        self.settings = load_settings()

        splitter = wx.SplitterWindow(self)
        self.canvas = NodeCanvas(splitter, self.on_node_selected, self.settings)

        # Right dock
        right = wx.Panel(splitter)
        rv = wx.BoxSizer(wx.VERTICAL)
        self.pg = wxpg.PropertyGridManager(right,
                                           style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_AUTO_SORT)
        self.pg.AddPage("Properties")
        rv.Add(self.pg, 1, wx.EXPAND | wx.ALL, 6)

        btns = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_add_in  = wx.Button(right, label="Add Input")
        self.btn_add_out = wx.Button(right, label="Add Output")
        btns.Add(self.btn_add_in,  1, wx.ALL, 4)
        btns.Add(self.btn_add_out, 1, wx.ALL, 4)
        rv.Add(btns, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        right.SetSizer(rv)

        splitter.SplitVertically(self.canvas, right, sashPosition=900)
        splitter.SetMinimumPaneSize(260)

        # Status bar + hotkeys
        self.CreateStatusBar()
        self.update_snap_status()
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)

        # Property bindings
        self.Bind(wxpg.EVT_PG_CHANGED, self.on_property_changed)
        self.btn_add_in.Bind(wx.EVT_BUTTON, self.on_add_input)
        self.btn_add_out.Bind(wx.EVT_BUTTON, self.on_add_output)

        self.selected_node = None
        self.Layout()
        self.Show()

    # -- UI helpers --

    def update_snap_status(self):
        state = "ON" if self.settings["snap_enabled"] else "OFF"
        self.SetTitle(f"Node Editor [Snap: {state}]")
        sb = self.GetStatusBar()
        if sb:
            sb.SetStatusText(f"Snap: {state}")

    # -- Selection & properties --

    def on_node_selected(self, node):
        self.selected_node = node
        self.pg.GetPage(0).Clear()
        if not node:
            return
        self.pg.Append(wxpg.StringProperty("Name", value=node.name))
        p_in = self.pg.Append(wxpg.LongStringProperty("Inputs", value="\n".join(node.inputs)))
        p_out = self.pg.Append(wxpg.LongStringProperty("Outputs", value="\n".join(node.outputs)))
        p_in.ChangeFlag(wxpg.PG_PROP_READONLY, True)
        p_out.ChangeFlag(wxpg.PG_PROP_READONLY, True)

    def on_property_changed(self, event):
        if not self.selected_node:
            return
        if event.GetProperty().GetName() == "Name":
            self.selected_node.name = event.GetProperty().GetValue()
            self.canvas.Refresh(False)

    def on_add_input(self, _):
        if not self.selected_node: return
        self.selected_node.inputs.append(f"Input {len(self.selected_node.inputs)+1}")
        self.on_node_selected(self.selected_node)
        self.canvas.Refresh(False)

    def on_add_output(self, _):
        if not self.selected_node: return
        self.selected_node.outputs.append(f"Output {len(self.selected_node.outputs)+1}")
        self.on_node_selected(self.selected_node)
        self.canvas.Refresh(False)

    # -- Save / load --

    def save_graph(self):
        dlg = wx.FileDialog(self, "Save graph", "", "", "JSON files (*.json)|*.json",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        data = {
            "nodes": [{
                "id": n.id,
                "name": n.name,
                "pos": [n.pos.x, n.pos.y],
                "inputs": n.inputs,
                "outputs": n.outputs
            } for n in self.canvas.nodes],
            "connections": [{
                "out": c.out_node.id,
                "out_index": c.out_index,
                "in": c.in_node.id,
                "in_index": c.in_index
            } for c in self.canvas.connections]
        }
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            wx.MessageBox(f"Error saving file:\n{ex}", "Error", wx.ICON_ERROR)
        dlg.Destroy()

    def load_graph(self):
        dlg = wx.FileDialog(self, "Open graph", "", "", "JSON files (*.json)|*.json", wx.FD_OPEN)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        try:
            with open(path) as f:
                data = json.load(f)

            self.canvas.nodes.clear()
            node_map = {}
            max_id = 0
            for nd in data.get("nodes", []):
                n = Node(nd["id"], nd.get("name", f"Node {nd['id']}"), nd.get("pos", [0, 0]))
                n.inputs = list(nd.get("inputs", []))
                n.outputs = list(nd.get("outputs", []))
                self.canvas.nodes.append(n)
                node_map[n.id] = n
                if n.id > max_id: max_id = n.id
            NodeCanvas.next_id = max(max_id + 1, NodeCanvas.next_id)

            self.canvas.connections.clear()
            for cd in data.get("connections", []):
                if cd.get("out") in node_map and cd.get("in") in node_map:
                    self.canvas.connections.append(Connection(
                        node_map[cd["out"]],
                        int(cd.get("out_index", 0)),
                        node_map[cd["in"]],
                        int(cd.get("in_index", 0)),
                    ))
            self.canvas.Refresh(False)
        except Exception as ex:
            wx.MessageBox(f"Error loading file:\n{ex}", "Error", wx.ICON_ERROR)
        dlg.Destroy()

    # -- Preferences & hotkeys --

    def open_preferences(self):
        dlg = PreferencesDialog(self, self.settings)
        if dlg.ShowModal() == wx.ID_OK:
            self.settings["snap_enabled"] = dlg.chk_snap.GetValue()
            self.settings["snap_size"] = dlg.spin_snap.GetValue()
            save_settings(self.settings)
            self.update_snap_status()
        dlg.Destroy()

    def OnKey(self, e):
        ctrl = e.ControlDown()
        code = e.GetKeyCode()
        if ctrl and code in (ord('S'), ord('s')):
            self.save_graph()
        elif ctrl and code in (ord('O'), ord('o')):
            self.load_graph()
        elif code == ord('G'):
            self.settings["snap_enabled"] = not self.settings["snap_enabled"]
            save_settings(self.settings)
            self.update_snap_status()
        else:
            e.Skip()

# ---------------- Run ----------------

if __name__ == "__main__":
    app = wx.App(False)
    NodeEditorFrame()
    app.MainLoop()
