import numpy.typing as npt

import solidedge.seconnect as se
import solidedge.utils as se_utils


def construct_plane(bounding_points: npt.ArrayLike) -> None:
    """Construct a plane from the bounding points"""
    doc = se.get_active_document()
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
    edges = body.Edges(se.constants.igQueryAll)
    sections = [edges.Item(1), edges.Item(2)]
    origins = [section.StartVertex for section in sections]

    blue_surf = blue_surfs.Add(2, sections, origins, se.constants.igNatural, 0, se.constants.igNatural, 0, 0, (),
                               se.constants.igNatural, 0, se.constants.igNatural, 0, False, False)

    # Cleanup
    se_utils.cleanup(drop_parents = blue_surf, delete = sketch_3d)
