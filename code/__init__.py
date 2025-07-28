# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 22:20:00 2025

@author: ekafex

Description:
    Initializes the camera_simulation package, exposing key modules and classes
    for screen-based camera calibration and simulation workflows.

Modules
-------
- display: Display modeling and calibration pattern generation
- camera_model: Camera intrinsic model and OpenCV-based calibration
- physical_model: Pendulum physics simulation
- simulation: Forward projection and noise simulation
- validation: Error metrics (reprojection, MSE)

Usage
-----
    from camera_simulation import Display, CameraCalibrator

    display = Display(width_m=0.344, height_m=0.193, width_px=1920, height_px=1080)
    calibrator = CameraCalibrator(square_size_mm=20, board_shape=(9, 6))

"""

from .display import Display, generate_checkerboard, show_checkerboard
from .camera_model import CameraModel, CameraCalibrator
from .physical_model import Pendulum, PendulumSimulator
from .simulation import simulate_camera_view, add_noise
from .validation import compute_reprojection_error, compute_mse

__all__ = [
    "Display",
    "generate_checkerboard",
    "show_checkerboard",
    "CameraModel",
    "CameraCalibrator",
    "Pendulum",
    "PendulumSimulator",
    "simulate_camera_view",
    "add_noise",
    "compute_reprojection_error",
    "compute_mse",
]
