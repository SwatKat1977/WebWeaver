"""
Copyright (C) 2025  Web Weaver Development Team
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of Web Weaver (https://github.com/SwatKat1977/WebWeaver).
See the LICENSE file in the project root for full license details.
"""
import math
import wx
from connection import Connection
from node import Node
from node_picker import NodePicker


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
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOTION, self._on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_mouse_leave)

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

    def _snap_val(self, v: float) -> float:
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

    def _on_paint(self, _):
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

        self.draw_grid(gc)
        self.draw_connections(gc)
        self.draw_nodes(gc)
        self.draw_temp_connection(gc)

        # Draw pin flashes
        self.draw_pin_flashes(gc)

    def draw_grid(self, gc):
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

    def draw_nodes(self, gc):
        """
        Draw all nodes in the canvas, including selection and shadow effects.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
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
            fill = n.color
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
        """
        Draw input and output pins for a node.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
            n (Node): The node whose pins are to be drawn.
        """
        pr = 5
        spacing = 20
        text_offset = 22

        # Inputs
        for i, label in enumerate(n.inputs):
            px = n.pos.x - 10
            py = n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(255, 100, 60)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            gc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                       wx.Colour(255, 255, 255))
            gc.DrawText(label, px + text_offset - 10, py - 7)

        # Outputs
        for i, label in enumerate(n.outputs):
            px = n.pos.x + n.size.width + 10
            py = n.pos.y + 30 + i * spacing
            gc.SetBrush(wx.Brush(wx.Colour(90, 210, 120)))
            gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 0)))
            gc.DrawEllipse(px - pr, py - pr, pr * 2, pr * 2)
            text_w, _, _, _ = gc.GetFullTextExtent(label)
            gc.DrawText(label, px - text_w - text_offset + 10, py - 7)

    def draw_connections(self, gc):
        """
        Draw all established connections between node pins.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
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
        """
        Draw a temporary connection line while the user is dragging
        from an output pin toward an input pin.

        Args:
            gc (wx.GraphicsContext): The graphics context used for drawing.
        """
        if not (self.dragging_connection and self.start_pin):
            return
        node, idx, _ = self.start_pin
        start = wx.RealPoint(node.pos.x + node.size.width + 10, node.pos.y + 30 + idx * 20)
        end = self._screen_to_world(self.last_mouse)
        gc.SetPen(wx.Pen(wx.Colour(220, 200, 100), 2, wx.PENSTYLE_DOT))
        d = abs(end.x - start.x) * 0.5
        path = gc.CreatePath()
        path.MoveToPoint(start.x, start.y)
        path.AddCurveToPoint(start.x + d, start.y, end.x - d, end.y, end.x, end.y)
        gc.StrokePath(path)

    # ----- Interaction -----

    def _on_left_down(self, event):
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
                px = n.pos.x + n.size.width + 10
                py = n.pos.y + 30 + i * 20
                if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
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

    def _on_left_up(self, event):
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
                    px = n.pos.x - 10
                    py = n.pos.y + 30 + i * 20
                    if (world.x - px) ** 2 + (world.y - py) ** 2 <= 6 ** 2:
                        # --- Remove any existing connections involving this pin pair ---
                        self.connections = [
                            c for c in self.connections
                            if not (
                                    (c.in_node == n and c.in_index == i) or
                                    (c.out_node == s_node and c.out_index == s_idx)
                            )
                        ]

                        # --- Add the new connection ---
                        self.connections.append(Connection(s_node, s_idx, n, i))

                        # --- Trigger the input flash effect ---
                        self.flash_pins.append([n, i, 6])

                        # Done — exit both loops
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

    def _on_mouse_move(self, event):
        """
        Handle mouse movement and dragging.

        Updates connection hover highlights, node dragging, or camera
        panning depending on the current interaction state.

        Args:
            event (wx.MouseEvent): The mouse event object.
        """
        world = self._screen_to_world(event.GetPosition())

        # Hover highlight
        for c in self.connections:
            n1, n2 = c.out_node, c.in_node
            p1 = wx.RealPoint(n1.pos.x + n1.size.width + 10, n1.pos.y + 30 + c.out_index * 20)
            p2 = wx.RealPoint(n2.pos.x - 10, n2.pos.y + 30 + c.in_index * 20)
            c.hovered = self.point_near_curve(world, p1, p2, tol=6)

        if event.Dragging() and event.LeftIsDown():
            if self.dragging_connection:
                self.last_mouse = event.GetPosition()
            elif self.drag_node:
                world_now = self._screen_to_world(event.GetPosition())
                delta = world_now - self.drag_anchor_world
                new_x = self.drag_anchor_node.x + delta.x
                new_y = self.drag_anchor_node.y + delta.y
                if self.settings["snap_enabled"]:
                    new_x = self._snap_val(new_x)
                    new_y = self._snap_val(new_y)
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

    def _on_mouse_wheel(self, event):
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

    def _on_context_menu(self, event):
        """
        Handles right-click context menu events in the node editor canvas.

        This method determines whether the user right-clicked on an existing
        connection or on empty space within the editor view, and displays
        the appropriate context menu or node picker popup.

        Behavior:
            - If the user right-clicks on a hovered connection, a context menu
              appears with the option to delete that connection.
            - If the user right-clicks on empty space, an Unreal-style node
              picker popup appears, allowing the user to add a new node at
              the clicked world position.

        Args:
            event (wx.ContextMenuEvent): The wx event triggered by a right-click.

        Side Effects:
            - May delete a connection if the user selects "Delete Connection".
            - May spawn a NodePicker popup for adding new nodes.
            - Schedules a delayed focus shift to the NodePicker's search box
              for reliable cross-platform UX.

        Notes:
            The `focus_search` function is called asynchronously via
            `wx.CallLater` to ensure the popup is active before setting focus,
            which improves behavior consistency across platforms.
        """
        world = self._screen_to_world(event.GetPosition())
        hovered_conn = next((c for c in self.connections if c.hovered), None)

        if hovered_conn:
            menu = wx.Menu()
            del_item = menu.Append(wx.ID_DELETE, "Delete Connection")
            self.Bind(wx.EVT_MENU,
                      lambda evt,
                      c=hovered_conn: self.__delete_connection(c),
                      del_item)
            self.PopupMenu(menu)
            menu.Destroy()
            return

        # Show Unreal-style node picker
        screen_pt = self.ClientToScreen(event.GetPosition())
        picker = NodePicker(self, world, self.add_node)
        picker.Position(screen_pt, (0, 0))
        picker.Popup()

        # Delay focus until popup is fully active (cross-platform reliable)
        def focus_search():
            if picker and picker.search:
                picker.Raise()
                picker.search.SetFocus()
                picker.search.SetInsertionPointEnd()

        wx.CallLater(100, focus_search)

    def _on_mouse_leave(self, _):
        """
        Handle mouse leaving the canvas area.

        Clears hover states for all connections and triggers a redraw.
        """
        for c in self.connections:
            c.hovered = False
        self.Refresh(False)

    # ----- Geometry helpers -----

    def point_near_curve(self, pt, p1, p2, tol=6):
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

    def add_node(self, node_type, pos):
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

    def draw_pin_flashes(self, gc):
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
