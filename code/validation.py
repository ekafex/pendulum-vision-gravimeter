# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 21:45:00 2025

@author: ekafex

Description:
    Provides basic validation and error analysis utilities for camera calibration
    and simulation. Includes reprojection error computation and pixel-wise mean
    squared error between images.

Dependencies:
    - numpy
    - opencv-python (for norm calculation)

Notes:
    - Errors are computed in pixel units unless otherwise specified.
    - TODO: Add advanced metrics (SSIM, perceptual loss, ML-based similarity)
"""

import numpy as np
import cv2


# --------------------------------------------------------
# Reprojection Error
# --------------------------------------------------------


def compute_reprojection_error(camera_model, object_points, image_points):
    """
    Compute mean reprojection error using camera model.

    Parameters
    ----------
    camera_model : CameraModel
        Calibrated camera model (K, distortion).
    object_points : list of np.ndarray
        3D points in world coordinates for each calibration image.
    image_points : list of np.ndarray
        Corresponding 2D detected points in image space.

    Returns
    -------
    mean_error : float
        Average reprojection error in pixels.
    """
    total_error = 0
    total_points = 0

    for objp, imgp, rvec, tvec in zip(
        object_points, image_points, camera_model.rvecs, camera_model.tvecs
    ):
        projected_points = camera_model.project_points(objp, rvec, tvec)
        error = cv2.norm(imgp, projected_points, cv2.NORM_L2) / len(projected_points)
        total_error += error
        total_points += 1

    return total_error / total_points if total_points > 0 else float("nan")


# --------------------------------------------------------
# Mean Squared Error (Pixel-Level)
# --------------------------------------------------------


def compute_mse(image1, image2):
    """
    Compute mean squared error (MSE) between two images.

    Parameters
    ----------
    image1 : np.ndarray
        First image (grayscale or color).
    image2 : np.ndarray
        Second image (same dimensions as image1).

    Returns
    -------
    mse : float
        Mean squared error (0 = perfect match).
    """
    # Ensure same shape
    if image1.shape != image2.shape:
        raise ValueError("Images must have the same shape for MSE computation.")

    diff = image1.astype(np.float32) - image2.astype(np.float32)
    mse = np.mean(diff**2)
    return mse


# --------------------------------------------------------
# TODO: Advanced Methods
# --------------------------------------------------------
# - Structural Similarity Index (SSIM) for perceptual quality
# - Multi-scale SSIM (MS-SSIM)
# - Learned perceptual metrics (LPIPS) or ML-based error prediction
# - Error heatmaps for spatial visualization
