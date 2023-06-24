from __future__ import annotations

import multiprocessing
from functools import partial
import numpy as np

from config import config


def get_normals_in_range(phi_0, phi_1, theta_0, theta_1, step):
    """Calculate vectors for a given segment of a sphere"""
    # Make sure number of steps is odd so that midpoint of the range is included in the angles
    phi_steps = int((phi_1 - phi_0) / 2 / step) * 2 + 1
    theta_steps = int((theta_1 - theta_0) / 2 / step) * 2 + 1

    phi = np.linspace(phi_0, phi_1, phi_steps)
    theta = np.linspace(theta_0, theta_1, theta_steps, endpoint = False)

    # Precompute sines and cosines
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    # Calculate all possible normals
    normals = np.array([
        [sp * ct, sp * st, cp] for sp, cp in zip(sin_phi, cos_phi) for st, ct in zip(sin_theta, cos_theta)
    ])

    return normals, phi, theta


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


def fit_cylinder_to_axis(w, num_points, mu, f0, f1, f2):
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


def fit_cylinder_in_range(fit_cylinder_partial, normals):
    """Fit cylinder along specified normal vectors and find the best one"""
    pool = multiprocessing.Pool()
    results = pool.map(fit_cylinder_partial, normals)

    # Get cylinder with the smallest error
    best_cylinder = min(results, key = lambda item: item[0])
    best_index = results.index(best_cylinder)
    _, r_sqr, center, normal = best_cylinder

    return best_index, r_sqr, center, normal


def fit_cylinder(points):
    """Fit cylinder through a set of points"""
    # Prepare data
    mean, centered_points, mu, f0, f1, f2 = preprocess(points)
    fit_cylinder_partial = partial(fit_cylinder_to_axis, num_points = len(points), mu = mu, f0 = f0, f1 = f1, f2 = f2)

    # Fit cylinders in steps
    phi_0 = 0
    phi_1 = np.pi / 2
    theta_0 = 0
    theta_1 = np.pi * 2
    r_sqr, center, normal = 0, 0, np.zeros(3)

    for i, angle_step in enumerate(config.cylinder_angle_steps):
        angle_step = float(np.radians(angle_step))

        # Find best cylinder in range
        normal_vectors, phi, theta = get_normals_in_range(phi_0, phi_1, theta_0, theta_1, angle_step)
        best_index, r_sqr, center, normal = fit_cylinder_in_range(fit_cylinder_partial, normal_vectors)

        # Calculate new range to search in
        if i < len(config.cylinder_angle_steps) - 1:
            # index of best phi and best theta comes from the list comprehensions with two loops 
            best_phi = phi[best_index // len(theta)]
            best_theta = theta[best_index % len(theta)]

            phi_0 = best_phi - angle_step
            phi_1 = best_phi + angle_step
            theta_0 = best_theta - angle_step
            theta_1 = best_theta + angle_step

    # Offset cylinder back to its original position
    center += mean

    # Calculate end point and length of the cylinder
    distances = np.dot(centered_points, normal)
    min_distance = np.min(distances)
    max_distance = np.max(distances)

    end_point = center + normal * min_distance
    length = max_distance - min_distance

    return normal, np.sqrt(r_sqr), end_point, length
