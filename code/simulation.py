# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 21:30:00 2025

@author: ekafex

Description:
    Provides utilities to generate synthetic camera images from world objects
    (e.g., checkerboard or pendulum trajectories) using a calibrated camera model.
    Supports adding realistic noise (Gaussian, Poisson) and simple motion blur.

Dependencies:
    - numpy
    - opencv-python
    - scipy.ndimage (for Gaussian filtering / blur)
    - display.py (for pattern generation)
    - camera_model.py (for projection and distortion)

Notes:
    - World coordinates must be provided in millimeters for correct projection.
    - Output images are in grayscale (0–255).
"""

import numpy as np
import cv2
from scipy.ndimage import gaussian_filter
from camera_model import CameraModel


# --------------------------------------------------------
# Utility: Add Noise
# --------------------------------------------------------


def add_noise(
    image: np.ndarray, gaussian_std=0.0, poisson_lambda=0.0, motion_blur=False
):
    """
    Add realistic noise to a synthetic image.

    Parameters
    ----------
    image : np.ndarray
        Grayscale image (0–255).
    gaussian_std : float
        Standard deviation of Gaussian noise to add.
    poisson_lambda : float
        Lambda parameter for Poisson noise (scaled to image intensity).
    motion_blur : bool
        Apply simple horizontal motion blur (3-pixel kernel).

    Returns
    -------
    noisy_image : np.ndarray
        Image with noise applied (clipped to 0–255).
    """
    noisy = image.astype(np.float32)

    # Gaussian noise
    if gaussian_std > 0:
        noisy += np.random.normal(0, gaussian_std, noisy.shape)

    # Poisson noise (simulate photon noise)
    if poisson_lambda > 0:
        scale = poisson_lambda / 255.0
        noisy = np.random.poisson(noisy * scale) / scale

    # Motion blur (simple horizontal kernel)
    if motion_blur:
        kernel = np.ones((1, 3)) / 3.0
        noisy = cv2.filter2D(noisy, -1, kernel)

    # Clip and convert back to uint8
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy


# --------------------------------------------------------
# Simulation: Project World Plane (Checkerboard)
# --------------------------------------------------------


def simulate_camera_view(
    camera: CameraModel,
    world_image: np.ndarray,
    world_size_mm: tuple,
    img_size_px: tuple,
    rvec: np.ndarray,
    tvec: np.ndarray,
    noise_params=None,
):
    """
    Simulate what the camera would capture of a planar world image.

    Parameters
    ----------
    camera : CameraModel
        Calibrated camera model.
    world_image : np.ndarray
        Grayscale image representing the world plane (0–1).
    world_size_mm : tuple
        Physical size of the world plane in mm (width, height).
    img_size_px : tuple
        Output image size (height, width) in pixels.
    rvec : np.ndarray
        Rotation vector for plane relative to camera.
    tvec : np.ndarray
        Translation vector for plane relative to camera.
    noise_params : dict, optional
        Parameters for noise model:
            {"gaussian_std": float, "poisson_lambda": float, "motion_blur": bool}

    Returns
    -------
    simulated_img : np.ndarray
        Simulated camera image (uint8, 0–255).
    """
    H_px, W_px = img_size_px

    # Generate 3D coordinates for world plane pixels
    H_w, W_w = world_image.shape
    # Create grid in world coordinates (mm)
    X = np.linspace(-world_size_mm[0] / 2, world_size_mm[0] / 2, W_w)
    Y = np.linspace(-world_size_mm[1] / 2, world_size_mm[1] / 2, H_w)
    XX, YY = np.meshgrid(X, Y)
    ZZ = np.zeros_like(XX)  # Plane at Z=0
    points_3d = np.stack([XX.ravel(), YY.ravel(), ZZ.ravel()], axis=1)  # (N,3)

    # Project points using camera model (distorted)
    projected = camera.project_points(points_3d, rvec, tvec)

    # Map projected points to image grid
    u = projected[:, 0].reshape(H_w, W_w)
    v = projected[:, 1].reshape(H_w, W_w)

    # Warp source image to camera image using OpenCV remap
    src_img = (world_image * 255).astype(np.uint8)
    map_x = u.astype(np.float32)
    map_y = v.astype(np.float32)
    simulated_img = cv2.remap(
        src_img,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )

    # Resize to target output resolution
    simulated_img = cv2.resize(simulated_img, (W_px, H_px))

    # Add noise if requested
    if noise_params:
        simulated_img = add_noise(
            simulated_img,
            gaussian_std=noise_params.get("gaussian_std", 0.0),
            poisson_lambda=noise_params.get("poisson_lambda", 0.0),
            motion_blur=noise_params.get("motion_blur", False),
        )

    return simulated_img
