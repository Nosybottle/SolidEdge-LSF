import numpy as np
import numpy.typing as npt
import logging

from config import lang


logger = logging.getLogger("LSF")


def plane_normal(centered_points: npt.ArrayLike) -> npt.NDArray:
    """Calculate normal vector of plane fitted through points centered around the origin"""
    # Singular Value Decomposition
    # Plane normal is the left singular vector with corresponding to the least singular value
    svd = np.linalg.svd(centered_points.T)
    left = svd[0]
    normal_vector = left[:, -1]

    return normal_vector


def plane_coordinate_system(normal_vector: npt.ArrayLike) -> npt.NDArray:
    """Create a coordinate system local to a plane"""
    # Construct a coordinate system oriented to the plane
    helper_vector = [1, 0, 0] if normal_vector[0] < normal_vector[2] else [0, 0, 1]
    y_axis = np.cross(normal_vector, helper_vector)
    x_axis = np.cross(y_axis, normal_vector)
    plane_cs = np.vstack((x_axis, y_axis, normal_vector))

    return plane_cs


def fit_plane(points: npt.ArrayLike) -> npt.NDArray:
    """Calculate best fit plane from the points and return bounding rectangle in the fitted plane"""
    logger.info(lang.info.plane_fitting)

    # Center the points around origin
    average = np.mean(points, axis = 0)
    centered_points = points - average

    normal_vector = plane_normal(centered_points)
    plane_cs = plane_coordinate_system(normal_vector)

    # Transform centered points to the plane coordinate systems and find their bounding rectangle
    plane_points = plane_cs @ centered_points.T
    x0, y0, _ = np.min(plane_points, axis = 1)
    x1, y1, _ = np.max(plane_points, axis = 1)
    bounding_rect = np.array([
        [x0, y0, 0],
        [x1, y0, 0],
        [x0, y1, 0],
        [x1, y1, 0]
    ])

    # Transform bounding rectangle back to the global CS
    plane_cs_inv = np.linalg.inv(plane_cs)
    global_bounding_rect = (plane_cs_inv @ bounding_rect.T).T
    global_bounding_rect += average

    return global_bounding_rect
