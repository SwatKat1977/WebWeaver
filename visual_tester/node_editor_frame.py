import json
import os
import wx
import wx.propgrid as wxpg
from node_canvas import NodeCanvas
from preferences_dialog import PreferencesDialog

class NodeEditorFrame(wx.Frame):
    CONFIG_PATH = os.path.expanduser("~/.weaver_settings.json")

    def __init__(self):
        super().__init__(None, title="Node Editor", size=(1200, 720))
        self.settings = self.load_settings()
        splitter = wx.SplitterWindow(self)
        self.canvas = NodeCanvas(splitter, self.on_node_selected, self.settings)

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

        self.CreateStatusBar()
        self.update_snap_status()
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)
        self.Bind(wxpg.EVT_PG_CHANGED, self.on_property_changed)
        self.btn_add_in.Bind(wx.EVT_BUTTON, self.on_add_input)
        self.btn_add_out.Bind(wx.EVT_BUTTON, self.on_add_output)
        self.selected_node = None
        self.Layout()
        self.Show()

    def update_snap_status(self):
        state = "ON" if self.settings["snap_enabled"] else "OFF"
        self.SetTitle(f"Node Editor [Snap: {state}]")
        sb = self.GetStatusBar()
        if sb:
            sb.SetStatusText(f"Snap: {state}")

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
            self.save_settings(self.settings)
            self.update_snap_status()
        else:
            e.Skip()

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
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        dlg.Destroy()

    def load_graph(self):
        dlg = wx.FileDialog(self, "Open graph", "", "", "JSON files (*.json)|*.json", wx.FD_OPEN)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
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
            max_id = max(max_id, n.id)
        NodeCanvas.next_id = max(max_id + 1, NodeCanvas.next_id)
        self.canvas.connections.clear()
        for cd in data.get("connections", []):
            if cd.get("out") in node_map and cd.get("in") in node_map:
                self.canvas.connections.append(Connection(
                    node_map[cd["out"]], int(cd["out_index"]),
                    node_map[cd["in"]], int(cd["in_index"])
                ))
        self.canvas.Refresh(False)
        dlg.Destroy()

    def load_settings(self):
        try:
            with open(self.CONFIG_PATH) as f:
                data = json.load(f)
                return {
                    "snap_enabled": bool(data.get("snap_enabled", False)),
                    "snap_size": int(data.get("snap_size", 20)),
                }
        except Exception:
            return {"snap_enabled": False, "snap_size": 20}


    def save_settings(self, data):
        try:
            with open(self.CONFIG_PATH, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            wx.LogError(f"Could not save settings: {ex}")

