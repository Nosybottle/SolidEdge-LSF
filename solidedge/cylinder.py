from solidedge.seconnect import seConstants, get_active_document


def construct_cylinder(direction, radius, origin, length) -> None:
    """Model a cylinder at specific point and orientation in space"""
    doc = get_active_document()
    if doc is None:
        return

    constructions = doc.Constructions
    ref_planes = doc.RefPlanes

    # Get plane normal to cylinder axis from it's origin
    sketch_3d = doc.Sketches3D.Add()
    lines_3d = sketch_3d.Lines3D
    line_3d = lines_3d.Add(*origin, *(origin + direction * length))

    edge = constructions.Item(constructions.Count).Body.Edges(seConstants.igQueryAll).Item(1)
    plane = ref_planes.AddNormalToCurve(edge, seConstants.igCurveStart, ref_planes.Item(1), seConstants.igPivotEnd)

    # Extrude cylinder
    sketch = doc.Sketches.Add()
    profile = sketch.Profiles.Add(plane)
    circles_2d = profile.Circles2d
    circles_2d.AddByCenterRadius(0, 0, radius)

    extrusions = constructions.ExtrudedSurfaces
    extrusion = extrusions.AddFinite(1, [profile], seConstants.igLeft, length)

    # Cleanup
    if doc.ModelingMode == seConstants.seModelingModeOrdered:
        extrusion.DropParents()
        sketch.Delete()
    line_3d.Delete()
    sketch_3d.Delete()
