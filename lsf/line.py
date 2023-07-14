import numpy as np
import numpy.typing as npt
import logging

from config import lang

logger = logging.getLogger("LSF")


def fit_line(points: npt.ArrayLike) -> tuple[npt.NDArray, npt.NDArray]:
    """Calculate best fit line through set of points"""
    logger.info(lang.info.line_fitting)

    mean = np.mean(points, axis = 0)

    uu, dd, vv = np.linalg.svd(points - mean)
    axis = vv[0]

    min_coords = np.min(points, axis = 0)
    max_coords = np.max(points, axis = 0)
    distance = np.linalg.norm(max_coords - min_coords)

    start_point = mean - axis * distance / 2
    end_point = mean + axis * distance / 2

    return start_point, end_point
