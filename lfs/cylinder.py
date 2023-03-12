import multiprocessing
from functools import partial
import numpy as np


def preprocess(points):
    """Precalculate values from a list of points"""
    mean = np.average(points, axis = 0)
    x = points - mean

    delta = np.ones((points.shape[0], 6))
    delta[:, 0] = x[:, 0] ** 2
    delta[:, 1] = 2 * x[:, 0] * x[:, 1]
    delta[:, 2] = 2 * x[:, 0] * x[:, 2]
    delta[:, 3] = x[:, 1] ** 2
    delta[:, 4] = 2 * x[:, 1] * x[:, 2]
    delta[:, 5] = x[:, 2] ** 2

    mu = np.average(delta, axis = 0)
    delta[:] -= mu

    f0 = np.zeros((3, 3))
    f1 = np.zeros((3, 6))
    f2 = np.zeros((6, 6))
    for x_i, d_i in zip(x, delta):
        f0 += np.outer(x_i, x_i)
        f1 += np.outer(x_i, d_i)
        f2 += np.outer(d_i, d_i)
    f0 /= len(x)
    f1 /= len(x)
    f2 /= len(x)

    return mean, x, mu, f0, f1, f2


def fit_cylinder_by_axis(w, num_points, mu, f0, f1, f2):
    """For a given axis try fitting a cylinder and return its parameters along with total error"""
    p = np.identity(3) - np.outer(w, w)
    s = np.array([
        [0, -w[2], w[1]],
        [w[2], 0, -w[0]],
        [-w[1], w[0], 0]
    ])

    a = p @ f0 @ p
    hat_a = -(s @ a @ s)
    hat_aa = hat_a @ a

    q = hat_a / np.trace(hat_aa)
    p_triangle = p[np.triu_indices(3)]
    alpha = f1 @ p_triangle
    beta = q @ alpha

    error = np.dot(p_triangle, f2 @ p_triangle) - 4 * np.dot(alpha, beta) + 4 * np.dot(beta, f0 @ beta)
    error /= num_points

    center = beta
    r_sqr = np.dot(p_triangle, mu) + np.dot(beta, beta)

    return error, r_sqr, center, w


def fit_cylinder(points):
    """Fit cylinder through a set of points"""
    mean, centered_points, mu, f0, f1, f2 = preprocess(points)

    # Uniformly distribute angles for testing cylinder axis vectors
    phi_steps = 90
    theta_steps = 360

    phi = np.linspace(0, np.pi / 2, phi_steps)  # [0, pi/2]
    theta = np.linspace(0, 2 * np.pi, theta_steps, endpoint = False)  # [0, 2 * pi)

    # Precompute sines and cosines
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    # Calculate all possible normals
    normals = np.array([
        [sp * ct, sp * st, cp] for sp, cp in zip(sin_phi, cos_phi) for st, ct in zip(sin_theta, cos_theta)
    ])

    pool = multiprocessing.Pool()
    cylinder_partial = partial(fit_cylinder_by_axis, num_points = len(points), mu = mu, f0 = f0, f1 = f1, f2 = f2)
    results = pool.map(cylinder_partial, normals)

    # Get cylinder with the smallest error
    _, r_sqr, center, normal = min(results, key = lambda item: item[0])
    center += mean

    # Calculate end point and length of the cylinder
    distances = np.dot(centered_points, normal)
    min_distance = np.min(distances)
    max_distance = np.max(distances)

    end_point = center + normal * min_distance
    length = max_distance - min_distance

    return normal, np.sqrt(r_sqr), end_point, length
