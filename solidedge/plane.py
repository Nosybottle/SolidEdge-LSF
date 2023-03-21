from solidedge.seconnect import seConstants, get_active_document


def construct_plane(bounding_points) -> None:
    """Construct a plane from the bounding points"""
    doc = get_active_document()
    if doc is None:
        return

    constructions = doc.Constructions
    blue_surfs = constructions.BlueSurfs
    sketches_3d = doc.Sketches3D

    # Draw opposite sides of the rectangle
    sketch_3d = sketches_3d.Add()
    lines_3d = sketch_3d.Lines3D
    lines_3d.Add(*bounding_points[0], *bounding_points[1])
    lines_3d.Add(*bounding_points[2], *bounding_points[3])

    # Connect them using BlueSurf
    body = constructions.Item(constructions.Count).Body
    edges = body.Edges(seConstants.igQueryAll)
    sections = [edges.Item(1), edges.Item(2)]
    origins = [section.StartVertex for section in sections]

    blue_surf = blue_surfs.Add(2, sections, origins, seConstants.igNatural, 0, seConstants.igNatural, 0, 0, (),
                               seConstants.igNatural, 0, seConstants.igNatural, 0, False, False)

    # Cleanup
    if doc.ModelingMode == seConstants.seModelingModeOrdered:
        blue_surf.DropParents()
    sketch_3d.Delete()
