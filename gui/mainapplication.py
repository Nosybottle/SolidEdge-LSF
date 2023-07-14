from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk

from config import lang
import lsf
import solidedge as se

logger = logging.getLogger("LSF")


class MainApplication(ttk.Frame):
    """Main graphical window of the application"""

    def __init__(self, mater, **kwargs):
        super().__init__(mater, **kwargs)
        mater.bind("<<OnClose>>", self.on_close)

        self.status_visible = False
        self.vertex_selector = se.VertexSelector()

        # Main frame
        self.f_controls = ttk.Frame(self)

        # Info label
        self.l_info = tk.Label(self, fg = "gray30")

        # Vertex selection gui
        self.lf_selector = ttk.Labelframe(self.f_controls, text = lang.selector.frame)
        self.b_start_selection = ttk.Button(self.lf_selector, text = lang.selector.start, command = self.run_selector)
        self.b_continue_selection = ttk.Button(self.lf_selector, text = lang.selector.continue_,
                                               command = self.continue_selector)
        self.b_stop_selection = ttk.Button(self.lf_selector, text = lang.selector.stop, command = self.stop_selector)
        self.l_counter = ttk.Label(self)

        # Surface fitting
        self.lf_surfaces = ttk.Labelframe(self.f_controls, text = lang.surfaces.frame)
        self.b_fit_plane = ttk.Button(self.lf_surfaces, text = lang.surfaces.plane,
                                      command = lambda: self.fit_object_to_points("plane"))
        self.b_fit_cylinder = ttk.Button(self.lf_surfaces, text = lang.surfaces.cylinder,
                                         command = lambda: self.fit_object_to_points("cylinder"))

        # Curve fitting
        self.lf_curves = ttk.Labelframe(self.f_controls, text = lang.curves.frame)
        self.b_fit_line = ttk.Button(self.lf_curves, text = lang.curves.line,
                                     command = lambda: self.fit_object_to_points("line"))
        self.b_fit_circle = ttk.Button(self.lf_curves, text = lang.curves.circle,
                                       command = lambda: self.fit_object_to_points("circle"))

        # Combined fitting
        self.lf_combined = ttk.Labelframe(self.f_controls, text = lang.combined.frame)
        self.b_fit_plane_circle = ttk.Button(self.lf_combined, text = f"{lang.surfaces.plane} + {lang.curves.circle}",
                                             command = lambda: self.fit_object_to_points("plane", "circle"))

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
        self.l_info.pack(padx = 12, pady = 4, side = "right")
        self.l_counter.pack(padx = 12, pady = 4, side = "left")

    def set_info_display(self, info_message: str = "") -> None:
        """Display info message in GUI"""
        self.l_info.configure(text = info_message)
        self.l_info.update()
        import time
        time.sleep(0.5)

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

    def fit_object_to_points(self, *fitting_objects: str) -> None:
        """Fit a specified object to points"""
        # Check enough points are selected
        for fitting_object in fitting_objects:
            if self.vertex_selector.count < lsf.required_points[fitting_object]:
                logger.error(lang.errors[f"{fitting_object}_points"])
                return

        points = self.vertex_selector.get_coordinates()
        self.clear()

        # Fit objects
        for fitting_object in fitting_objects:
            fitting_function = getattr(lsf, f"fit_{fitting_object}")
            drawing_function = getattr(se, f"construct_{fitting_object}")

            fitting_data = fitting_function(points)
            if isinstance(fitting_data, tuple):
                drawing_function(*fitting_data)
            else:
                drawing_function(fitting_data)

        logger.info(lang.info.done)
