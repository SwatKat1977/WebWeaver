"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import math
import wx
from connection import Connection
from node import Node, NodeCategory
from node_picker import NodePicker
from node_types import NodeShape


class ExecutionNode:
    def __init__(self, node):
        self.node = node  # reference to the visual Node
        self.children = []

    def __repr__(self):
        return f"ExecutionNode({self.node.name}, children={len(self.children)})"


class NodeCanvas(wx.Panel):
    """
    A custom wx.Panel that provides a visual, interactive node editor canvas.

    The NodeCanvas supports adding, connecting, and arranging nodes in a
    graph-like layout. Users can pan, zoom, create connections between
    nodes, and invoke context menus for node or connection actions.
    """
    # pylint: disable=too-many-instance-attributes
    next_id = 100

    def __init__(self, parent, on_node_selected, settings):
        """
        Initialize the node canvas and its interaction state.

        Args:
            parent (wx.Window): The parent window or panel.
            on_node_selected (Callable): Callback triggered when a node is selected.
            settings (dict): Dictionary containing editor settings such as
                             'snap_size' and 'snap_enabled'.
        """
        super().__init__(parent, style=wx.WANTS_CHARS)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.on_node_selected = on_node_selected
        self.settings = settings
        self.flash_pins = []  # list of (node, input_index, time_remaining)
        self.active_picker = None

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

        # Anchor points for snapping
        self.drag_anchor_world = None
        self.drag_anchor_node = None

        # Events
        self.Bind(wx.EVT_PAINT, self.__on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.__on_left_up)
        self.Bind(wx.EVT_MOTION, self.__on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self.__on_mouse_wheel)
        self.Bind(wx.EVT_CONTEXT_MENU, self.__on_context_menu)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.__on_mouse_leave)

    def get_execution_tree(self):
        node_lookup = {n.id: n for n in self.nodes}

        adjacency = {}
        for c in self.connections:
            # store tuples: (out_index, in_node.id)
            adjacency.setdefault(c.out_node.id, []).append((c.out_index, c.in_node.id))

        start_node = next((n for n in self.nodes if n.category == NodeCategory.START), None)
        if not start_node:
            raise ValueError("No Start node found")

        exec_tree = self._build_execution_tree(start_node, adjacency, node_lookup)

        # For debugging: show the whole thing
        self.print_execution_tree(exec_tree)

        return exec_tree

    def _build_execution_tree(self,
                              start_node,
                              adjacency,
                              node_lookup,
                              visited=None):
        if visited is None:
            visited = set()
        if start_node.id in visited:
            return None  # avoid cycles
        visited.add(start_node.id)

        exec_node = ExecutionNode(start_node)

        for out_index, child_id in adjacency.get(start_node.id, []):
            child_node = node_lookup[child_id]
            child_exec = self._build_execution_tree(child_node, adjacency, node_lookup, visited.copy())
            if child_exec:
                # Keep output label and ExecutionNode together
                label = ""
                if out_index < len(start_node.outputs):
                    label = start_node.outputs[out_index]
                exec_node.children.append((label, child_exec))

        return exec_node

    def print_execution_tree(self, node, indent="", is_last=True, seen=None):
        if node is None:
            return
        if seen is None:
            seen = set()

        name = getattr(node.node, "name", None) or getattr(node.node, "node_type", "") or str(node.node.id)
        prefix = "└── " if is_last else "├── "
        print(indent + prefix + name)

        # Prevent expanding the same node twice
        if node.node.id in seen:
            print(indent + "    ↳ [shared node]")
            return
        seen.add(node.node.id)

        new_indent = indent + ("    " if is_last else "│   ")

        # Each child in node.children is (edge_label, child_exec_node)
        for i, (edge_label, child) in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            if edge_label:
                print(new_indent + f"({edge_label})")  # print parent → child label once here
            self.print_execution_tree(child, new_indent, is_last_child, seen)

    # ----- Helpers -----

    def _screen_to_world(self, pt: wx.Point) -> wx.RealPoint:
        """
        Convert a screen coordinate to world-space coordinates.

        Args:
            pt (wx.Point): A point in screen (pixel) coordinates.

        Returns:
            wx.RealPoint: The corresponding point in world coordinates,
                          adjusted for offset and zoom scale.
        """
        return wx.RealPoint(
            (pt.x - self.offset.x) / self.scale,
            (pt.y - self.offset.y) / self.scale
        )

    def __snap_grid_value(self, v: float) -> float:
        """
        Snap a value to the nearest grid step if snapping is enabled.

        Args:
            v (float): The value to be snapped.

        Returns:
            float: The snapped value based on the snap size setting.
        """
        s = max(1, int(self.settings["snap_size"]))
        return round(v / s) * s

    # ----- Paint -----

    def __on_paint(self, _):
        """
        Handle paint events for the node canvas.

        Draws the background, grid, nodes, connections, temporary
        connections (during drags), and visual effects such as pin flashes.
        """
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetClientSize()

        gc.SetBrush(wx.Brush(wx.Colour(28, 29, 33)))
        gc.DrawRectangle(0, 0, w, h)

        gc.Translate(self.offset.x, self.offset.y)
        gc.Scale(self.scale, self.scale)

        self.__draw_grid(gc)
        self.__draw_connections(gc)
        self.__draw_nodes(gc)
        self.__draw_temp_connection(gc)

        # Draw pin flashes
        self.__draw_pin_flashes(gc)

    def __draw_grid(self, gc):
        """
        Draw the background grid with minor and major gridlines.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
        # pylint: disable=too-many-locals
        w, h = self.GetClientSize()

        # Minor step = snap size; major every 2 minors
        step_minor = max(5, int(self.settings.get("snap_size", 20)))  # e.g. 20
        major_every = 2  # 2*20 = 40 (bold)

        tl = self._screen_to_world(wx.Point(0, 0))
        br = self._screen_to_world(wx.Point(w, h))

        start_x = math.floor(tl.x / step_minor) * step_minor
        end_x = math.ceil(br.x / step_minor) * step_minor
        start_y = math.floor(tl.y / step_minor) * step_minor
        end_y = math.ceil(br.y / step_minor) * step_minor

        pen_minor = wx.Pen(wx.Colour(45, 46, 50))
        pen_major = wx.Pen(wx.Colour(60, 61, 65))

        # verticals
        i = int(round(start_x / step_minor))
        x = start_x
        while x <= end_x:
            gc.SetPen(pen_major if (i % major_every) == 0 else pen_minor)
            gc.StrokeLine(x, start_y, x, end_y)
            x += step_minor
            i += 1

        # horizontals
        j = int(round(start_y / step_minor))
        y = start_y
        while y <= end_y:
            gc.SetPen(pen_major if (j % major_every) == 0 else pen_minor)
            gc.StrokeLine(start_x, y, end_x, y)
            y += step_minor
            j += 1

    def __draw_nodes(self, gc):
        for n in self.nodes:
            r = n.rect()

            # ---- Shadow (soft) ----
            if n.shape == NodeShape.CIRCLE:
                gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 60)))  # softer shadow
                gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
                gc.DrawEllipse(r.x + 3, r.y + 3, r.width - 1, r.height - 1)
            else:
                gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 100)))
                gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
                gc.DrawRoundedRectangle(r.x + 6, r.y + 6, r.width, r.height, 10)

            # ---- Category glow (optional) ----
            if n.category == NodeCategory.START:
                glow = wx.Colour(80, 255, 80, 50)
            elif n.selected:
                glow = wx.Colour(255, 140, 0, 80)
            else:
                glow = None

            if glow:
                gc.SetBrush(wx.Brush(glow))
                gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
                if n.shape == NodeShape.CIRCLE:
                    gc.DrawEllipse(r.x - 3, r.y - 3, r.width + 6, r.height + 6)
                else:
                    gc.DrawRoundedRectangle(r.x - 4, r.y - 4, r.width + 8, r.height + 8, 12)

            # ---- Body ----
            border = wx.Colour(255, 140, 0) if n.selected else wx.Colour(60, 62, 68)
            gc.SetBrush(wx.Brush(n.color))
            gc.SetPen(wx.Pen(border, 2))
            if n.shape == NodeShape.CIRCLE:
                gc.DrawEllipse(r.x, r.y, r.width, r.height)
            else:
                gc.DrawRoundedRectangle(r.x, r.y, r.width, r.height, 10)

            # ---- Label ----
            gc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                       n.label_color)
            if n.category not in [NodeCategory.START,]:
                text_w, text_h, _, _ = gc.GetFullTextExtent(n.name)
                if n.shape == NodeShape.CIRCLE:
                    gc.DrawText(n.name, r.x + (r.width - text_w) / 2, r.y + (r.height - text_h) / 2)
                else:
                    gc.DrawText(n.name, r.x + 10, r.y + 8)

            # ---- Pins ----
            self.__draw_pins(gc, n)

    def __draw_pins(self, gc, n: Node):
        """
        Draw input and output pins for a node.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
            n (Node): The node whose pins are to be drawn.
        """
        pr = 5
        text_offset = 22

        # START: output only (centered)
        if n.category == NodeCategory.START:
            p = self.__calculate_pin_position(n, 'out', 0)
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(p.x - pr, p.y - pr, pr * 2, pr * 2)
            return

        # NORMAL: inputs
        gc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                   wx.Colour(255, 255, 255))
        for i, label in enumerate(n.inputs):
            p = self.__calculate_pin_position(n, 'in', i)
            gc.SetBrush(wx.Brush(wx.Colour(255, 100, 60)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(p.x - pr, p.y - pr, pr * 2, pr * 2)
            if label:
                gc.DrawText(label, p.x + text_offset - 10, p.y - 7)

        # NORMAL: outputs
        for i, label in enumerate(n.outputs):
            p = self.__calculate_pin_position(n, 'out', i)
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(p.x - pr, p.y - pr, pr * 2, pr * 2)
            if label:
                text_w, _, _, _ = gc.GetFullTextExtent(label)
                gc.DrawText(label, p.x - text_w - text_offset + 10, p.y - 7)

    def __draw_connections(self, gc):
        """
        Draw all established connections between node pins.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
        for c in self.connections:
            p1 = self.__calculate_pin_position(c.out_node, 'out', c.out_index)
            p2 = self.__calculate_pin_position(c.in_node, 'in', c.in_index)
            d = abs(p2.x - p1.x) * 0.5
            colour = wx.Colour(255, 255, 255) if c.hovered else wx.Colour(160, 160, 160)
            gc.SetPen(wx.Pen(colour, 2))
            path = gc.CreatePath()
            path.MoveToPoint(p1.x, p1.y)
            path.AddCurveToPoint(p1.x + d, p1.y, p2.x - d, p2.y, p2.x, p2.y)
            gc.StrokePath(path)

    def __draw_temp_connection(self, gc):
        """
        Draw a temporary connection line while the user is dragging
        from an output pin toward an input pin.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
        if self.dragging_connection and self.start_pin:
            node, idx, _ = self.start_pin
            start = self.__calculate_pin_position(node, 'out', idx)
            end = self._screen_to_world(self.last_mouse)
            gc.SetPen(wx.Pen(wx.Colour(220, 200, 100), 2, wx.PENSTYLE_DOT))
            d = abs(end.x - start.x) * 0.5
            path = gc.CreatePath()
            path.MoveToPoint(start.x, start.y)
            path.AddCurveToPoint(start.x + d, start.y, end.x - d, end.y, end.x, end.y)
            gc.StrokePath(path)

    # ----- Interaction -----

    def __on_left_down(self, event):
        """
        Handle left mouse button press.

        Begins dragging a node or initiates a connection drag if the user
        clicks on an output pin. Also updates node selection state.

        Args:
            event (wx.MouseEvent): The mouse event object.
        """
        self.CaptureMouse()
        self.last_mouse = event.GetPosition()
        world = self._screen_to_world(self.last_mouse)

        # Start connection drag
        for n in reversed(self.nodes):
            for i, _ in enumerate(n.outputs):
                p = self.__calculate_pin_position(n, 'out', i)
                if (world.x - p.x) ** 2 + (world.y - p.y) ** 2 <= 6 ** 2:
                    self.dragging_connection = True
                    self.start_pin = (n, i, "out")
                    self.SetFocus()
                    self.Refresh(False)
                    return

        clicked = None
        for n in reversed(self.nodes):
            r = n.rect()
            if (r.x <= world.x <= r.x + r.width) and (r.y <= world.y <= r.y + r.height):
                clicked = n
                break

        for n in self.nodes:
            n.selected = n == clicked
        self.on_node_selected(clicked)

        self.drag_node = clicked
        self.dragging = True
        if self.drag_node:
            self.drag_anchor_world = self._screen_to_world(self.last_mouse)
            self.drag_anchor_node = wx.RealPoint(self.drag_node.pos.x, self.drag_node.pos.y)

        self.SetFocus()
        self.Refresh(False)

    def __on_left_up(self, event):
        """
        Handle left mouse button release.

        Finalizes dragging of nodes or connections, establishes new
        connections if appropriate, and resets drag state.

        Args:
            event (wx.MouseEvent): The mouse event object.
        """
        if self.HasCapture():
            self.ReleaseMouse()

        if self.dragging_connection and self.start_pin:
            world = self._screen_to_world(event.GetPosition())
            s_node, s_idx, _ = self.start_pin

            for n in self.nodes:
                for i, _ in enumerate(n.inputs):
                    p = self.__calculate_pin_position(n, 'in', i)
                    if (world.x - p.x) ** 2 + (world.y - p.y) ** 2 <= 6 ** 2:
                        # remove conflicting connections
                        self.connections = [
                            c for c in self.connections
                            if not (
                                    (c.in_node == n and c.in_index == i) or
                                    (c.out_node == s_node and c.out_index == s_idx)
                            )
                        ]
                        self.connections.append(Connection(s_node, s_idx, n, i))
                        self.flash_pins.append([n, i, 6])
                        break
                else:
                    continue
                break

        # --- Always cleanup ---
        self.dragging = False
        self.drag_node = None
        self.dragging_connection = False
        self.start_pin = None
        self.drag_anchor_world = None
        self.drag_anchor_node = None
        self.Refresh(False)

    def __on_mouse_move(self, event):
        """
        Handle mouse movement and dragging.

        Updates connection hover highlights, node dragging, or camera
        panning depending on the current interaction state.

        Args:
            event (wx.MouseEvent): The mouse event object.
        """
        # --- Node hover detection ---
        hovered = None
        world = self._screen_to_world(event.GetPosition())

        # Convert world (RealPoint) -> wx.Point for hit testing
        world_pt = wx.Point(int(world.x), int(world.y))

        for n in self.nodes:
            r = n.rect()
            n.hovered = r.Contains(world_pt)
            if n.hovered:
                hovered = n

        self.hovered_node = hovered

        # Hover highlight
        for c in self.connections:
            p1 = self.__calculate_pin_position(c.out_node, 'out', c.out_index)
            p2 = self.__calculate_pin_position(c.in_node, 'in', c.in_index)
            c.hovered = self.__point_near_curve(world, p1, p2, tol=6)

        if event.Dragging() and event.LeftIsDown():
            if self.dragging_connection:
                self.last_mouse = event.GetPosition()
            elif self.drag_node:
                world_now = self._screen_to_world(event.GetPosition())
                delta = world_now - self.drag_anchor_world
                new_x = self.drag_anchor_node.x + delta.x
                new_y = self.drag_anchor_node.y + delta.y
                if self.settings["snap_enabled"]:
                    new_x = self.__snap_grid_value(new_x)
                    new_y = self.__snap_grid_value(new_y)
                self.drag_node.pos.x = new_x
                self.drag_node.pos.y = new_y
            else:
                delta = event.GetPosition() - self.last_mouse
                self.offset.x += delta.x
                self.offset.y += delta.y
                self.last_mouse = event.GetPosition()
        else:
            self.last_mouse = event.GetPosition()

        self.Refresh(False)

    def __on_mouse_wheel(self, event):
        """
        Handle zooming using the mouse wheel.

        Zooms in or out centered around the mouse cursor, maintaining
        the cursor’s world position under the zoom.

        Args:
            event (wx.MouseEvent): The mouse wheel event.
        """
        delta = event.GetWheelRotation() / event.GetWheelDelta()
        zoom = 1.1 if delta > 0 else 0.9
        mouse = event.GetPosition()
        before = self._screen_to_world(mouse)
        self.scale = max(0.3, min(2.5, self.scale * zoom))
        after = self._screen_to_world(mouse)
        self.offset.x += (after.x - before.x) * self.scale
        self.offset.y += (after.y - before.y) * self.scale
        self.Refresh(False)

    def __on_context_menu(self, event):
        pt_screen = wx.GetMousePosition()
        pt_client = self.ScreenToClient(pt_screen)
        mouse_screen = wx.GetMousePosition()

        if self.hovered_node:
            node = self.hovered_node
            menu = wx.Menu()

            if not node.is_protected():
                delete_item = menu.Append(wx.ID_DELETE, "Delete Node")
                self.Bind(
                    wx.EVT_MENU,
                    lambda _evt, n=node: self.__delete_node(n),
                    delete_item
                )

            self.PopupMenu(menu)
            menu.Destroy()
            return

        # delete-connection menu
        hovered_conn = next((c for c in self.connections if getattr(c, "hovered", False)), None)
        if hovered_conn:
            menu = wx.Menu()
            del_item = menu.Append(wx.ID_DELETE, "Delete Connection")
            self.Bind(wx.EVT_MENU, lambda _e, c=hovered_conn: self.__delete_connection(c), del_item)
            self.PopupMenu(menu)
            menu.Destroy()
            return

        # close any open picker
        if getattr(self, "active_picker", None) and self.active_picker.IsShown():
            self.active_picker.Close()
            self.active_picker = None

        def add_from_picker(node_type, _pos):
            # Reverse the transform used in OnPaint
            world_x = (pt_client.x - self.offset.x) / self.scale
            world_y = (pt_client.y - self.offset.y) / self.scale
            world_point = wx.RealPoint(world_x, world_y)

            self.__add_node(node_type, world_point)

        # show picker at mouse
        popup_point = wx.Point(mouse_screen.x - 10, mouse_screen.y - 10)
        self.active_picker = NodePicker(self, popup_point, add_from_picker)
        self.active_picker.Show()

        wx.CallLater(
            100,
            lambda: (
                self.active_picker.Raise(),
                self.active_picker.search.SetFocus(),
                self.active_picker.search.SetInsertionPointEnd()
            )
        )

    def __on_mouse_leave(self, _):
        """
        Handle mouse leaving the canvas area.

        Clears hover states for all connections and triggers a redraw.
        """
        for c in self.connections:
            c.hovered = False
        self.Refresh(False)

    # ----- Geometry helpers -----

    def __point_near_curve(self, pt, p1, p2, tol=6):
        """
        Check if a point lies within a given tolerance of a Bezier curve.

        Args:
            pt (wx.RealPoint): The test point.
            p1 (wx.RealPoint): The start point of the curve.
            p2 (wx.RealPoint): The end point of the curve.
            tol (float, optional): The distance threshold in world units.

        Returns:
            bool: True if the point is near the curve; otherwise False.
        """
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

    def __delete_connection(self, c):
        """
        Delete a connection from the canvas and refresh the display.

        Args:
            c (Connection): The connection to be deleted.
        """
        if c in self.connections:
            self.connections.remove(c)
            self.Refresh(False)

    def __add_node(self, node_type, pos):
        """
        Add a new node to the canvas at a given position.

        Args:
            node_type (str): The type or name of the node to create.
            pos (wx.RealPoint): The world position where the node is placed.
        """
        n = Node(NodeCanvas.next_id, node_type, (pos.x, pos.y))

        NodeCanvas.next_id += 1
        self.nodes.append(n)
        self.Refresh(False)

    def __draw_pin_flashes(self, gc):
        """
        Draw fading highlights for recently connected pins.

        This provides a short visual feedback effect to indicate a successful
        connection creation. The flash gradually fades and triggers periodic
        redraws until fully expired.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
        if not self.flash_pins:
            return

        new_flashes = []
        for n, i, t in self.flash_pins:
            if t <= 0:
                continue
            px = n.pos.x - 10
            py = n.pos.y + 30 + i * 20
            radius = 5 + (6 - t)
            alpha = int(255 * (t / 6))
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120, alpha)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(px - radius, py - radius, radius * 2, radius * 2)
            new_flashes.append([n, i, t - 1])

        self.flash_pins = new_flashes

        # Schedule next redraw if any flashes remain
        if self.flash_pins:
            wx.CallLater(50, self.Refresh, False)

    def __delete_node(self, node):
        """Remove a node from the canvas, unless it's protected."""
        if node.is_protected():
            wx.LogMessage(f"Cannot delete protected node: {node.name}")
            return

        # Also delete connections attached to this node
        self.connections = [
            c for c in self.connections
            if c.in_node != node and c.out_node != node
        ]

        # Remove from the node list
        self.nodes.remove(node)
        self.Refresh(False)

    def __calculate_pin_position(self, n, kind: str, index: int) -> wx.RealPoint:
        """
        Return the world-space position of a pin.
        kind: 'in' or 'out'
        index: pin index on that side
        """
        # horizontal anchor
        if kind == "in":
            x = n.pos.x - 10
        else:
            x = n.pos.x + n.size.width + 10

        # vertical anchor
        if n.category == NodeCategory.START and kind == "out":
            y = n.pos.y + n.size.height / 2

        else:
            y = n.pos.y + 30 + index * 20

        return wx.RealPoint(x, y)