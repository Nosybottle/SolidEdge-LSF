import numpy.typing as npt

import solidedge.seconnect as se
import solidedge.utils as se_utils


def construct_line(start_point: npt.ArrayLike, end_point: npt.ArrayLike) -> None:
    """Create a line between two points"""
    doc = se.get_active_document()
    if doc is None:
        return
    sketches_3d = doc.Sketches3D

    # Draw line
    sketch_3d = sketches_3d.Add()
    lines_3d = sketch_3d.Lines3D
    lines_3d.Add(*start_point, *end_point)

    derived_curve = se_utils.derive_curve()
    se_utils.cleanup(drop_parents = derived_curve, delete = sketch_3d)
