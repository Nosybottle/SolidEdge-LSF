from __future__ import annotations

from tkinter import ttk

from solidedge.vertexselector import VertexSelector


class MainApplication(ttk.Frame):
    """Main graphical window of the application"""

    def __init__(self, mater, **kwargs):
        super().__init__(mater, **kwargs)
        mater.bind("<<OnClose>>", self.on_close)

        self.vertex_selector: None | VertexSelector = None

        self.b_start_selection = ttk.Button(text = "Run selector", command = self.run_selector)
        self.b_stop_selection = ttk.Button(text = "Stop selector", command = self.stop_selector)
        self.b_get_points = ttk.Button(text = "Získej body", command = self.get_points)

        self.b_start_selection.pack()
        self.b_stop_selection.pack()
        self.b_get_points.pack()

    def run_selector(self) -> None:
        """Start vertex selection"""
        print("Starting selection...")
        self.vertex_selector = VertexSelector()
        self.process_events()

    def process_events(self) -> None:
        """Start loop processing the vertex selector events"""
        if self.vertex_selector is None:
            return

        if self.vertex_selector.is_done():
            self.vertex_selector.clear_highlight()
            print("Done selecting...")
            return

        self.vertex_selector.process_events()
        self.after(100, self.process_events)

    def stop_selector(self) -> None:
        """Stop the vertex selection"""
        if self.vertex_selector is None:
            return

        print("Terminating selection...")
        self.vertex_selector.terminate()
        self.vertex_selector.clear_highlight()
        self.vertex_selector = None

    def on_close(self, *_) -> None:
        """When the application is closing terminate the mouse event"""
        self.stop_selector()

    def get_points(self):
        """Get coordinates of the selected points"""
        if self.vertex_selector is None:
            return

        points = self.vertex_selector.get_coordinates()
        print(points)
