import numpy.typing as npt
import logging

import solidedge.seconnect as se
import solidedge.utils as se_utils
from config import lang

logger = logging.getLogger("LSF")


def construct_circle(normal: npt.ArrayLike, center: npt.ArrayLike, r):
    """Construct a circle in 3D"""
    logger.info(lang.info.circle_construction)

    doc = se.get_active_document()
    if doc is None:
        return
    sketches_3d = doc.Sketches3D

    # Draw circle
    sketch_3d = sketches_3d.Add()
    ellipses_3d = sketch_3d.Ellipses3D
    ellipses_3d.AddByCenterRadiusNormal(*center, *normal, r)

    derived_curve = se_utils.derive_curve()
    se_utils.cleanup(drop_parents = derived_curve, delete = sketch_3d)
