import numpy.typing as npt

import solidedge.seconnect as se


def construct_line(start_point: npt.ArrayLike, end_point: npt.ArrayLike) -> None:
    """Create a line between two points"""
    doc = se.get_active_document()
    if doc is None:
        return

    constructions = doc.Constructions
    derived_curves = constructions.DerivedCurves
    sketches_3d = doc.Sketches3D

    # Draw opposite sides of the rectangle
    sketch_3d = sketches_3d.Add()
    lines_3d = sketch_3d.Lines3D
    lines_3d.Add(*start_point, *end_point)

    # Derive curve
    body = constructions.Item(constructions.Count).Body
    body_edges = body.Edges(se.constants.igQueryAll)
    edges = [body_edges.Item(1)]
    derived_curve = derived_curves.Add(1, edges, se.constants.igDCComposite)

    # Cleanup
    if doc.ModelingMode == se.constants.seModelingModeOrdered:
        derived_curve.DropParents()
    sketch_3d.Delete()
