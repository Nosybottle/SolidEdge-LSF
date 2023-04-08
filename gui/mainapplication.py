from __future__ import annotations

import logging
from tkinter import ttk

from config import lang
from lfs import fit_plane, fit_cylinder
from solidedge import VertexSelector, construct_plane, construct_cylinder

logger = logging.getLogger("LSF")


class MainApplication(ttk.Frame):
    """Main graphical window of the application"""

    def __init__(self, mater, **kwargs):
        super().__init__(mater, **kwargs)
        mater.bind("<<OnClose>>", self.on_close)

        self.status_visible = False
        self.vertex_selector = VertexSelector()

        # Main frame
        self.f_controls = ttk.Frame(self)

        # Status label
        self.s_status = ttk.Separator(self)
        self.l_status = ttk.Label(self)

        # Vertex selection gui
        self.lf_selector = ttk.Labelframe(self.f_controls, text = lang.selector.frame)
        self.b_start_selection = ttk.Button(self.lf_selector, text = lang.selector.start, command = self.run_selector)
        self.b_continue_selection = ttk.Button(self.lf_selector, text = lang.selector.continue_,
                                               command = self.continue_selector)
        self.b_stop_selection = ttk.Button(self.lf_selector, text = lang.selector.stop, command = self.stop_selector)
        self.l_counter = ttk.Label(self)

        # Surface fitting
        self.lf_surfaces = ttk.Labelframe(self.f_controls, text = lang.surfaces.frame)
        self.b_fit_plane = ttk.Button(self.lf_surfaces, text = lang.surfaces.plane, command = self.fit_plane)
        self.b_fit_cylinder = ttk.Button(self.lf_surfaces, text = lang.surfaces.cylinder, command = self.fit_cylinder)

        self.layout_widgets()
        self.update_counter()

    def layout_widgets(self) -> None:
        """Layout all widgets to be displayed"""
        # Label frames
        label_frames = [item for item in vars(self).values() if isinstance(item, ttk.LabelFrame)]
        for i, label_frame in enumerate(label_frames):
            if i == 0:
                padx = (12, 4)
            elif i == len(label_frames) - 1:
                padx = (4, 12)
            else:
                padx = 4
            label_frame.pack(padx = padx, pady = (9, 0), ipady = 2, side = "left", anchor = "n")

        # Buttons
        buttons = (item for item in vars(self).values() if isinstance(item, ttk.Button))
        for button in buttons:
            button.pack(padx = 6, pady = 2, ipadx = 6, fill = "x")

        # Other
        self.f_controls.pack(side = "top")
        self.l_counter.pack(padx = 12, pady = (2, 4), side = "top", anchor = "w")

    def show_status(self) -> None:
        """Display status label and separator"""
        self.l_status.pack(side = "bottom", anchor = "w", padx = 12, pady = (3, 4))
        self.s_status.pack(side = "bottom", padx = 9, fill = "x")

    def display_message(self, message: str) -> None:
        """Display message to the user"""
        if not self.status_visible:
            self.show_status()
            self.status_visible = True
        self.l_status.configure(text = message)

    def update_counter(self) -> None:
        """Update selected vertices counter"""
        count = self.vertex_selector.count
        self.l_counter.configure(text = f"{lang.selector.counter} {count}")

    def process_events(self) -> None:
        """Start loop processing the vertex selector events"""
        if self.vertex_selector.is_done():
            self.vertex_selector.clear_highlight()
            return

        self.vertex_selector.process_events()
        self.update_counter()
        self.after(100, self.process_events)

    def run_selector(self) -> None:
        """Start vertex selection"""
        self.vertex_selector.new_selection()
        self.process_events()

    def continue_selector(self) -> None:
        """Continue stopped selector"""
        self.vertex_selector.continue_selection()
        self.process_events()

    def stop_selector(self) -> None:
        """Stop the vertex selection"""
        self.vertex_selector.stop()

    def clear(self) -> None:
        """Clear selector"""
        self.vertex_selector.clear()
        self.stop_selector()
        self.update_counter()

    def on_close(self, *_) -> None:
        """When the application is closing terminate the mouse event"""
        self.stop_selector()

    def fit_plane(self):
        """Fit plane through the selected points"""
        points = self.vertex_selector.get_coordinates()
        if points is None:
            return
        if len(points) < 6:
            logger.error(lang.errors.plane_points)
            return

        self.clear()

        bounding_rectangle = fit_plane(points)
        construct_plane(bounding_rectangle)

    def fit_cylinder(self):
        """Fit cylinder through the selected points"""
        points = self.vertex_selector.get_coordinates()
        if points is None:
            return
        if len(points) < 6:
            logger.error(lang.errors.cylinder_points)
            return

        self.clear()

        normal_vector, radius, end_point, length = fit_cylinder(points)
        construct_cylinder(normal_vector, radius, end_point, length)
