from __future__ import annotations

import numpy as np
import numpy.typing as npt
import logging
import win32com.client
import win32gui  # noqa
from pywintypes import com_error  # noqa

from solidedge import se
from config import lang

logger = logging.getLogger("LSF")


def rgb_to_int(r, g, b):
    return r + (g << 8) + (b << 16)


class VertexSelector:
    """Class for handling Solid Edge mouse events allowing the user to select 3D points"""

    def __init__(self) -> None:
        self.vertices = {}
        self.start_drag: None | tuple[float, float] = None
        self.end_drag: None | tuple[float, float] = None

        self.doc = None
        self.window = None
        self.view = None
        self.highlight_set = None
        self.command = None
        self.mouse = None

    def new_selection(self) -> None:
        """Clean old and start new vertex selection"""
        if not self.create_command(clear_data = True):
            return

        logger.info(lang.info.selector_new)

    def continue_selection(self) -> None:
        """Continue selection with current vertices"""
        if self.highlight_set is not None:
            self.clear_highlight()
        if not self.create_command(clear_data = False):
            return
        self.highlight_all()

        logger.info(lang.info.selector_continue)

    def stop(self) -> None:
        """Terminate the mouse event"""
        if self.command is None:
            return

        self.clear_highlight()
        se.app.AbortCommand(True)

        self.window = None
        self.view = None
        self.highlight_set = None
        self.command = None
        self.mouse = None

        logger.info(lang.info.selector_stop)

    def create_command(self, clear_data: bool) -> bool:
        """Create new SolidEdge command to select vertices. Return success of creating new command"""
        active_document = se.get_active_document()
        if active_document is None:
            return False

        if clear_data or not self.working_document_is_active_document(active_document):
            self.clear()

        self.doc = active_document
        self.window = se.app.ActiveWindow
        self.view = self.window.View

        self.highlight_set = self.doc.HighlightSets.Add()
        self.highlight_set.Color = rgb_to_int(0, 127, 0)

        self.command = se.app.CreateCommand(se.constants.seNoDeactivate)
        self.command.Start()

        self.mouse = self.command.Mouse
        self.mouse.LocateMode = 1
        self.mouse.EnabledDrag = True
        self.mouse.ScaleMode = 0
        self.mouse.WindowTypes = 1
        self.mouse.AddToLocateFilter(se.constants.seLocatePoint)

        self.register_events()

        return True

    def register_events(self) -> None:
        """Register the necessary Solid Edge events.
        MouseEvents is defined within the function to allow access to a VertexSelector instance"""

        # Method names are the same as the mouse Event prefixed with "On"
        # Defining MouseEvents class inside a function gives it access to the VertexSelector object via "self"
        # noinspection PyPep8Naming
        class MouseEvents:
            @staticmethod
            def OnMouseDown(*args) -> None:
                """When mouse is clicked pass the event to the Vertex Selector to handle"""
                self.mouse_down(*args)

            @staticmethod
            def OnMouseDrag(*args) -> None:
                """When mouse is dragged pass the event to the Vertex Selector to handle"""
                self.mouse_drag(*args)

        win32com.client.WithEvents(self.mouse, MouseEvents)

    def working_document_is_active_document(self, active_document) -> bool:
        """Check whether saved document is the currently active one"""
        # if active_document is None:
        #     return False
        return self.doc == active_document

    @staticmethod
    def process_events() -> None:
        """Process waiting event messages. This should be called in a loop"""
        win32gui.PumpWaitingMessages()

    def is_done(self) -> bool:
        """Is the command done? Accessing the 'Done' attribute when the command is actually done raises an error"""
        # Command is already destroyed, it must be done
        if self.command is None:
            return True

        try:
            return self.command.Done
        except com_error:
            return True

    @staticmethod
    def get_body_vertices(model) -> list:
        """Return all vertices af a model"""
        vertices = []
        try:
            body = model.Body
            if body.Visible:
                vertices += [body.Vertices.Item(i) for i in range(1, body.Vertices.Count + 1)]
        # When bodies are united/stitched they may not be accessible though they are listed/counted
        except Exception as e:
            print(e)

        return vertices

    def get_visible_vertices(self) -> list:
        """Get all vertices of a document and save them for fence selection"""
        visible_vertices = []

        # Design bodies
        models = self.doc.Models
        for i in range(1, models.Count + 1):
            model = models.Item(i)
            visible_vertices += self.get_body_vertices(model)

        # Construction bodies and surfaces, curves, 3D sketches
        constructions = self.doc.Constructions
        for i in range(1, constructions.Count + 1):
            construction = constructions.Item(i)
            visible_vertices += self.get_body_vertices(construction)

        # 2D sketches
        sketches = self.doc.Sketches
        for i in range(1, sketches.Count + 1):
            sketch = sketches.Item(i)
            profile = sketch.Profile
            if profile.Visible:
                curve_vertices = profile.CurveBody.CurveVertices
                visible_vertices += [curve_vertices.Item(i) for i in range(1, curve_vertices.Count + 1)]

        return visible_vertices

    def mouse_down(self, button, modifier, _dx, _dy, _dz, _p_window_dispatch, _l_key_point_type,
                   p_graphic_dispatch) -> None:
        """Process MouseDown event. If clicked on a vertex, add it to the selected vertices"""
        if button != 1:
            return
        if p_graphic_dispatch is None:
            return

        self.process_vertex(p_graphic_dispatch, modifier)

    def mouse_drag(self, button, modifier, dx, dy, _dz, _p_window_dispatch, drag_state, _l_key_point_type,
                   p_graphic_dispatch) -> None:
        """Process MouseDrag event. When drag is ended determine which vertices lie in the selected area and add them"""
        if button != 1:
            return

        if p_graphic_dispatch is not None:
            self.process_vertex(p_graphic_dispatch, modifier)

        if drag_state == 0:
            self.start_drag = (dx, dy)
        elif drag_state == 2:
            self.end_drag = (dx, dy)
            vertices = self.fence_select()
            for vertex in vertices:
                self.process_vertex(vertex, modifier)

    def fence_select(self) -> list:
        """Find all points in the fenced area and add them"""
        x_min, x_max = sorted((self.start_drag[0], self.end_drag[0]))
        y_min, y_max = sorted((self.start_drag[1], self.end_drag[1]))

        vertices = []
        for vertex in self.get_visible_vertices():
            vertex_coords = tuple(vertex.GetPointData(tuple()))
            x, y = self.view.TransformModelToDC(*vertex_coords, 0, 0)

            if (x_min <= x <= x_max) and (y_min <= y <= y_max):
                vertices.append(vertex)
        return vertices

    def process_vertex(self, vertex, modifier) -> None:
        """Determine what should be done with the selected vertex based on the modifier key held"""
        vertex = se.geometry.Vertex(vertex)

        if modifier == 2:  # CTRL
            self.remove_vertex(vertex)
        else:
            self.add_vertex(vertex)

    def add_vertex(self, vertex) -> None:
        """Highlight the selected vertex"""
        if vertex.Tag in self.vertices:
            return

        self.vertices[vertex.Tag] = vertex
        self.highlight_set.AddItem(vertex)
        self.highlight_set.Draw()

    def remove_vertex(self, vertex) -> None:
        """Highlight the selected vertex"""
        if vertex.Tag not in self.vertices:
            return

        index = list(self.vertices).index(vertex.Tag) + 1
        self.highlight_set.RemoveItem(index)
        self.highlight_set.Draw()
        del self.vertices[vertex.Tag]

    def clear(self) -> None:
        """Clear selected vertices"""
        self.vertices.clear()
        self.clear_highlight()

    def highlight_all(self) -> None:
        """Highlight all saved vertices"""
        for vertex in self.vertices.values():
            self.highlight_set.AddItem(vertex)
        self.highlight_set.Draw()

    def clear_highlight(self) -> None:
        """Clear highlighted vertices"""
        if not se.is_document_open(self.doc):
            return

        if self.highlight_set is not None:
            self.highlight_set.RemoveAll()
            self.highlight_set.Draw()

    def get_coordinates(self) -> npt.NDArray | None:
        """Get 3D coordinates of the selected vertices"""
        # No document is active, return nothing
        active_document = se.get_active_document()
        if active_document is None:
            return

        # Working document isn't the active one, return 0 selected points
        if not self.working_document_is_active_document(active_document):
            return np.array([])

        points = [vertex.GetPointData(tuple()) for vertex in self.vertices.values()]
        return np.array(points)

    @property
    def count(self) -> int:
        """Return number of selected vertices"""
        return len(self.vertices)
