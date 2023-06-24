import numpy.typing as npt

import solidedge.seconnect as se


def construct_cylinder(direction: npt.ArrayLike, radius: float, origin: npt.ArrayLike, length: float) -> None:
    """Model a cylinder at specific point and orientation in space"""
    doc = se.get_active_document()
    if doc is None:
        return

    constructions = doc.Constructions
    ref_planes = doc.RefPlanes

    # Get plane normal to cylinder axis from it's origin
    sketch_3d = doc.Sketches3D.Add()
    lines_3d = sketch_3d.Lines3D
    line_3d = lines_3d.Add(*origin, *(origin + direction * length))

    ref_plane = ref_planes.Item(1) if all(direction != [0, 0, 1]) else ref_planes.Item(2)
    edge = constructions.Item(constructions.Count).Body.Edges(se.constants.igQueryAll).Item(1)
    plane = ref_planes.AddNormalToCurve(edge, se.constants.igCurveStart, ref_plane, se.constants.igPivotEnd)

    # Extrude cylinder
    sketch = doc.Sketches.Add()
    profile = sketch.Profiles.Add(plane)
    circles_2d = profile.Circles2d
    circles_2d.AddByCenterRadius(0, 0, radius)

    extrusions = constructions.ExtrudedSurfaces
    extrusion = extrusions.AddFinite(1, [profile], se.constants.igLeft, length)

    # Cleanup
    if doc.ModelingMode == se.constants.seModelingModeOrdered:
        extrusion.DropParents()
        sketch.Delete()
    line_3d.Delete()
    sketch_3d.Delete()
