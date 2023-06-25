import numpy.typing as npt

import solidedge.seconnect as se


def construct_circle(normal: npt.ArrayLike, center: npt.ArrayLike, r):
    """Construct a circle in 3D"""
    doc = se.get_active_document()
    if doc is None:
        return

    constructions = doc.Constructions
    derived_curves = constructions.DerivedCurves
    sketches_3d = doc.Sketches3D

    # Draw the circle
    sketch_3d = sketches_3d.Add()
    ellipses_3d = sketch_3d.Ellipses3D
    ellipses_3d.AddByCenterRadiusNormal(*center, *normal, r)

    # Derive curve
    body = constructions.Item(constructions.Count).Body
    body_edges = body.Edges(se.constants.igQueryAll)
    edges = [body_edges.Item(1)]
    derived_curve = derived_curves.Add(1, edges, se.constants.igDCComposite)

    # Cleanup
    if doc.ModelingMode == se.constants.seModelingModeOrdered:
        derived_curve.DropParents()
    sketch_3d.Delete()
