import wx
import wx.propgrid as wxpg
import math, json, os

# ----------------------------------------------------------
#  Node / Connection Model
# ----------------------------------------------------------

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

    def get_rect(self):
        return wx.Rect(int(self.pos.x), int(self.pos.y), self.size.width, self.size.height)


class Connection:
    def __init__(self, out_node, out_index, in_node, in_index):
        self.out_node = out_node
        self.out_index = out_index
        self.in_node = in_node
        self.in_index = in_index
        self.hovered = False


# ----------------------------------------------------------
#  Canvas
# ----------------------------------------------------------

class NodeCanvas(wx.Panel):
    next_id = 100

    def __init__(self, parent, on_node_selected):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.on_node_selected = on_node_selected

        self.nodes = []
        self.connections = []

        # camera
        self.scale = 1.0
        self.offset = wx.RealPoint(0, 0)

        # mouse state
        self.dragging = False
        self.last_mouse = wx.Point(0, 0)
        self.drag_node = None
        self.dragging_connection = False
        self.start_pin = None

        # events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    # ----------------------------------------------------------
    #  Coordinate helpers
    # ----------------------------------------------------------

    def screen_to_world(self, pt):
        return wx.RealPoint((pt.x - self.offset.x) / self.scale, (pt.y - self.offset.y) / self.scale)

    # ----------------------------------------------------------
    #  Paint
    # ----------------------------------------------------------

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

    # ----------------------------------------------------------
    #  Drawing
    # ----------------------------------------------------------

    def draw_grid(self, gc):
        w, h = self.GetClientSize()
        step = 40
        tl = self.screen_to_world(wx.Point(0, 0))
        br = self.screen_to_world(wx.Point(w, h))
        start_x = math.floor(tl.x / step) * step
        end_x = math.ceil(br.x / step) * step
        start_y = math.floor(tl.y / step) * step
        end_y = math.ceil(br.y / step) * step
        fine = wx.Pen(wx.Colour(45, 46, 50))
        bold = wx.Pen(wx.Colour(60, 61, 65))
        for i, x in enumerate(range(int(start_x), int(end_x) + 1, step)):
            gc.SetPen(bold if i % 5 == 0 else fine)
            gc.StrokeLine(x, start_y, x, end_y)
        for j, y in enumerate(range(int(start_y), int(end_y) + 1, step)):
            gc.SetPen(bold if j % 5 == 0 else fine)
            gc.StrokeLine(start_x, y, end_x, y)

    def draw_nodes(self, gc):
        for n in self.nodes:
            r = n.get_rect()

            # shadow
            gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 130)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawRoundedRectangle(r.x + 6, r.y + 6, r.width, r.height, 10)

            # selection glow
            if n.selected:
                glow = wx.Colour(255, 140, 0, 80)
                gc.SetBrush(wx.Brush(glow))
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

    def draw_pins(self, gc, n):
        pr = 5
        spacing = 20
        text_offset = 22

        # inputs
        for i, label in enumerate(n.inputs):
            px, py = n.pos.x - 10, n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(255, 100, 60)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            gc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                       wx.Colour(255, 255, 255))
            gc.DrawText(label, px + text_offset - 10, py - 7)

        # outputs
        for i, label in enumerate(n.outputs):
            px, py = n.pos.x + n.size.width + 10, n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            text = gc.GetFullTextExtent(label)
            gc.DrawText(label, px - text[0] - text_offset + 10, py - 7)

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

    # ----------------------------------------------------------
    #  Interaction
    # ----------------------------------------------------------

    def OnLeftDown(self, e):
        self.CaptureMouse()
        self.last_mouse = e.GetPosition()
        world = self.screen_to_world(self.last_mouse)

        # start connection?
        for n in reversed(self.nodes):
            for i, _ in enumerate(n.outputs):
                px, py = n.pos.x + n.size.width + 10, n.pos.y + 30 + i * 20
                if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
                    self.dragging_connection = True
                    self.start_pin = (n, i, "out")
                    self.Refresh(False)
                    return

        # select node
        clicked = None
        for n in reversed(self.nodes):
            r = n.get_rect()
            if r.x <= world.x <= r.x + r.width and r.y <= world.y <= r.y + r.height:
                clicked = n
                break
        for n in self.nodes:
            n.selected = (n == clicked)
        self.on_node_selected(clicked)
        self.drag_node = clicked
        self.dragging = True
        self.Refresh(False)

    def OnLeftUp(self, e):
        if self.HasCapture():
            self.ReleaseMouse()
        if self.dragging_connection and self.start_pin:
            world = self.screen_to_world(e.GetPosition())
            for n in self.nodes:
                for i, _ in enumerate(n.inputs):
                    px, py = n.pos.x - 10, n.pos.y + 30 + i * 20
                    if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
                        s, idx, _ = self.start_pin
                        self.connections.append(Connection(s, idx, n, i))
                        break
        self.dragging_connection = False
        self.start_pin = None
        self.dragging = False
        self.drag_node = None
        self.Refresh(False)

    def OnMouseMove(self, e):
        wpt = self.screen_to_world(e.GetPosition())

        for c in self.connections:
            n1, n2 = c.out_node, c.in_node
            p1 = wx.RealPoint(n1.pos.x + n1.size.width + 10, n1.pos.y + 30 + c.out_index * 20)
            p2 = wx.RealPoint(n2.pos.x - 10, n2.pos.y + 30 + c.in_index * 20)
            c.hovered = self.point_near_curve(wpt, p1, p2, 6)

        if e.Dragging() and e.LeftIsDown():
            if self.dragging_connection:
                self.last_mouse = e.GetPosition()
            elif self.drag_node:
                d = self.screen_to_world(e.GetPosition()) - self.screen_to_world(self.last_mouse)
                self.drag_node.pos.x += d.x
                self.drag_node.pos.y += d.y
                self.last_mouse = e.GetPosition()
            else:
                d = e.GetPosition() - self.last_mouse
                self.offset.x += d.x
                self.offset.y += d.y
                self.last_mouse = e.GetPosition()
        else:
            self.last_mouse = e.GetPosition()
        self.Refresh(False)

    def OnMouseWheel(self, e):
        delta = e.GetWheelRotation() / e.GetWheelDelta()
        f = 1.1 if delta > 0 else 0.9
        m = e.GetPosition()
        before = self.screen_to_world(m)
        self.scale = max(0.3, min(2.5, self.scale * f))
        after = self.screen_to_world(m)
        self.offset.x += (after.x - before.x) * self.scale
        self.offset.y += (after.y - before.y) * self.scale
        self.Refresh(False)

    def OnContextMenu(self, e):
        world = self.screen_to_world(e.GetPosition())
        hovered_conn = next((c for c in self.connections if c.hovered), None)
        menu = wx.Menu()
        if hovered_conn:
            del_item = menu.Append(wx.ID_DELETE, "Delete Connection")
            self.Bind(wx.EVT_MENU, lambda evt, c=hovered_conn: self.delete_connection(c), del_item)
        else:
            add_item = menu.Append(-1, "Add Node Here")
            self.Bind(wx.EVT_MENU, lambda evt, pos=world: self.add_node("Node", pos), add_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def delete_connection(self, c):
        if c in self.connections:
            self.connections.remove(c)
            self.Refresh(False)

    def add_node(self, name, pos):
        node = Node(NodeCanvas.next_id, name, (pos.x, pos.y))
        NodeCanvas.next_id += 1
        self.nodes.append(node)
        self.Refresh(False)

    def point_near_curve(self, pt, p1, p2, tol=6):
        steps, mind = 20, 1e9
        d = abs(p2.x - p1.x) * 0.5
        for s in [i / steps for i in range(steps + 1)]:
            bx = ((1 - s) ** 3) * p1.x + 3 * ((1 - s) ** 2) * s * (p1.x + d) + \
                 3 * (1 - s) * (s ** 2) * (p2.x - d) + (s ** 3) * p2.x
            by = ((1 - s) ** 3) * p1.y + 3 * ((1 - s) ** 2) * s * p1.y + \
                 3 * (1 - s) * (s ** 2) * p2.y + (s ** 3) * p2.y
            mind = min(mind, math.hypot(pt.x - bx, pt.y - by))
        return mind <= tol


# ----------------------------------------------------------
#  Frame with Property Panel and Save/Load
# ----------------------------------------------------------

class NodeEditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Node Editor", size=(1200, 700))
        splitter = wx.SplitterWindow(self)
        self.canvas = NodeCanvas(splitter, self.on_node_selected)

        # property panel
        right = wx.Panel(splitter)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.pg = wxpg.PropertyGridManager(right,
                                           style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_AUTO_SORT)
        self.pg.AddPage("Properties")

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_add_input = wx.Button(right, label="Add Input")
        self.btn_add_output = wx.Button(right, label="Add Output")
        btn_box.Add(self.btn_add_input, 1, wx.ALL, 5)
        btn_box.Add(self.btn_add_output, 1, wx.ALL, 5)
        vbox.Add(self.pg, 1, wx.EXPAND | wx.ALL, 5)
        vbox.Add(btn_box, 0, wx.EXPAND | wx.ALL, 5)
        right.SetSizer(vbox)
        splitter.SplitVertically(self.canvas, right, sashPosition=900)
        splitter.SetMinimumPaneSize(300)

        # bindings
        self.Bind(wxpg.EVT_PG_CHANGED, self.on_property_changed)
        self.btn_add_input.Bind(wx.EVT_BUTTON, self.on_add_input)
        self.btn_add_output.Bind(wx.EVT_BUTTON, self.on_add_output)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.selected_node = None
        self.Show()

    # ----------------------------------------------------------
    #  Property updates
    # ----------------------------------------------------------

    def on_node_selected(self, node):
        self.selected_node = node
        self.pg.GetPage(0).Clear()
        if not node:
            return
        self.pg.Append(wxpg.StringProperty("Name", value=node.name))
        self.pg.Append(wxpg.LongStringProperty("Inputs", value="\n".join(node.inputs)))
        self.pg.Append(wxpg.LongStringProperty("Outputs", value="\n".join(node.outputs)))

    def on_property_changed(self, e):
        if not self.selected_node:
            return
        prop = e.GetProperty()
        name = prop.GetName()
        value = prop.GetValue()
        if name == "Name":
            self.selected_node.name = value
        elif name == "Inputs":
            self.selected_node.inputs = [i.strip() for i in value.split("\n") if i.strip()]
        elif name == "Outputs":
            self.selected_node.outputs = [o.strip() for o in value.split("\n") if o.strip()]
        self.canvas.Refresh(False)

    def on_add_input(self, _):
        if self.selected_node:
            self.selected_node.inputs.append(f"Input {len(self.selected_node.inputs) + 1}")
            self.on_node_selected(self.selected_node)
            self.canvas.Refresh(False)

    def on_add_output(self, _):
        if self.selected_node:
            self.selected_node.outputs.append(f"Output {len(self.selected_node.outputs) + 1}")
            self.on_node_selected(self.selected_node)
            self.canvas.Refresh(False)

    # ----------------------------------------------------------
    #  Save / Load
    # ----------------------------------------------------------

    def on_key(self, e):
        key = e.GetKeyCode()
        ctrl = e.ControlDown()
        if ctrl and key in (ord('S'), ord('s')):
            self.save_graph()
        elif ctrl and key in (ord('O'), ord('o')):
            self.load_graph()
        else:
            e.Skip()

    def save_graph(self):
        dlg = wx.FileDialog(self, "Save graph", "", "", "JSON files (*.json)|*.json", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "pos": [n.pos.x, n.pos.y],
                    "inputs": n.inputs,
                    "outputs": n.outputs
                } for n in self.canvas.nodes
            ],
            "connections": [
                {
                    "out": c.out_node.id,
                    "out_index": c.out_index,
                    "in": c.in_node.id,
                    "in_index": c.in_index
                } for c in self.canvas.connections
            ]
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
            for ndata in data.get("nodes", []):
                n = Node(ndata["id"], ndata["name"], ndata["pos"])
                n.inputs, n.outputs = ndata.get("inputs", []), ndata.get("outputs", [])
                self.canvas.nodes.append(n)
                node_map[n.id] = n
            self.canvas.connections.clear()
            for cdata in data.get("connections", []):
                if cdata["out"] in node_map and cdata["in"] in node_map:
                    self.canvas.connections.append(Connection(
                        node_map[cdata["out"]],
                        cdata["out_index"],
                        node_map[cdata["in"]],
                        cdata["in_index"]
                    ))
            self.canvas.Refresh(False)
        except Exception as ex:
            wx.MessageBox(f"Error loading file:\n{ex}", "Error", wx.ICON_ERROR)
        dlg.Destroy()


# ----------------------------------------------------------
#  Run
# ----------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(False)
    NodeEditorFrame()
    app.MainLoop()
