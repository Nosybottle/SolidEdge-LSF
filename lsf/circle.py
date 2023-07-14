import numpy as np
import numpy.typing as npt
import logging

from lsf import plane
from config import lang


logger = logging.getLogger("LSF")


def fit_circle(points: npt.ArrayLike):
    """Fit specified points by a circle in 3D"""
    logger.info(lang.info.circle_fitting)

    mean = np.mean(points, axis = 0)
    centered_points = points - mean

    # Calculate plane normal and transform points to the plane coordinate system
    plane_normal = plane.plane_normal(centered_points)
    plane_cs = plane.plane_coordinate_system(plane_normal)
    plane_points = plane_cs @ centered_points.T

    # Fit circle
    x, y, _ = plane_points
    A = np.array([x, y, np.ones(len(x))]).T
    b = x ** 2 + y ** 2

    c = np.linalg.lstsq(A, b, rcond = None)[0]
    local_center = np.array([c[0] / 2, c[1] / 2, 0])
    r = np.sqrt(c[2] + (c[0] / 2) ** 2 + (c[1] / 2) ** 2)

    plane_cs_inv = np.linalg.inv(plane_cs)
    center = (plane_cs_inv @ local_center).T
    center += mean

    return plane_normal, center, r
