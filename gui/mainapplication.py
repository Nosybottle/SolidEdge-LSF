from __future__ import annotations

from tkinter import ttk

from lfs import fit_plane, fit_cylinder
from solidedge import VertexSelector, construct_plane, construct_cylinder


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
        self.lf_selector = ttk.Labelframe(self.f_controls, text = "Vertex selector")
        self.b_start_selection = ttk.Button(self.lf_selector, text = "New selection", command = self.run_selector)
        self.b_continue_selection = ttk.Button(self.lf_selector, text = "Continue",
                                               command = self.continue_selector)
        self.b_stop_selection = ttk.Button(self.lf_selector, text = "Stop", command = self.stop_selector)
        self.l_counter = ttk.Label(self.lf_selector, text = "Selected vertices: 0")

        # Surface fitting
        self.lf_surfaces = ttk.Labelframe(self.f_controls, text = "Surfaces")
        self.b_fit_plane = ttk.Button(self.lf_surfaces, text = "Fit plane", command = self.fit_plane)
        self.b_fit_cylinder = ttk.Button(self.lf_surfaces, text = "Fit cylinder", command = self.fit_cylinder)

        self.layout_widgets()

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
            label_frame.pack(padx = padx, pady = 9, ipady = 2, side = "left", anchor = "n")

        # Buttons
        buttons = (item for item in vars(self).values() if isinstance(item, ttk.Button))
        for button in buttons:
            button.pack(padx = 6, pady = 2, fill = "x")

        # Other
        self.f_controls.pack(side = "top")
        self.l_counter.pack(padx = 6, anchor = "w")

    def show_status(self) -> None:
        """Display status label and separator"""
        self.l_status.pack(side = "bottom", anchor = "w", padx = 12, pady = (3, 6))
        self.s_status.pack(side = "bottom", padx = 9, fill = "x")

    def display_message(self, message: str) -> None:
        """Display message to the user"""
        if not self.status_visible:
            self.show_status()
            self.status_visible = True
        self.l_status.configure(text = message)

    def process_events(self) -> None:
        """Start loop processing the vertex selector events"""
        if self.vertex_selector.is_done():
            self.vertex_selector.clear_highlight()
            print("Done selecting...")
            return

        self.vertex_selector.process_events()
        self.after(100, self.process_events)

    def run_selector(self) -> None:
        """Start vertex selection"""
        print("Starting selection...")
        self.vertex_selector.new_selection()
        self.process_events()

    def continue_selector(self) -> None:
        """Continue stopped selector"""
        print("Continuing selection...")
        self.vertex_selector.continue_selection()
        self.process_events()

    def stop_selector(self) -> None:
        """Stop the vertex selection"""
        print("Terminating selection...")
        self.vertex_selector.stop()

    def on_close(self, *_) -> None:
        """When the application is closing terminate the mouse event"""
        self.stop_selector()

    def fit_plane(self):
        """Fit plane through the selected points"""
        points = self.vertex_selector.get_coordinates()
        self.stop_selector()

        bounding_rectangle = fit_plane(points)
        construct_plane(bounding_rectangle)

    def fit_cylinder(self):
        """Fit cylinder through the selected points"""
        points = self.vertex_selector.get_coordinates()
        self.stop_selector()

        normal_vector, radius, end_point, length = fit_cylinder(points)
        construct_cylinder(normal_vector, radius, end_point, length)
