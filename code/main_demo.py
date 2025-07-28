# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 22:00:00 2025

@author: ekafex

Description:
    Demonstrates a complete workflow:
        1. Generate checkerboard for on-screen calibration
        2. Calibrate camera using captured images
        3. Simulate pendulum trajectory in 3D
        4. Project trajectory onto camera image (forward simulation)
        5. Validate using reprojection error and MSE

Dependencies:
    - numpy
    - matplotlib
    - opencv-python
    - scipy
    - Modules: display, camera_model, physical_model, simulation, validation
"""

import numpy as np
import cv2
from display import Display, generate_checkerboard, show_checkerboard
from camera_model import CameraCalibrator
from physical_model import Pendulum, PendulumSimulator
from simulation import simulate_camera_view
from validation import compute_reprojection_error, compute_mse

# --------------------------------------------------------
# 1. Define display and generate checkerboard
# --------------------------------------------------------

# Physical properties of monitor (example: ThinkPad E570)
display = Display(width_m=0.344, height_m=0.193, width_px=1920, height_px=1080)

# Generate checkerboard
checker_img, square_size_mm = generate_checkerboard(display, squares=(9, 6))
show_checkerboard(checker_img, display)

# --------------------------------------------------------
# 2. Calibrate camera using real images
# --------------------------------------------------------

# Assume you have captured calibration images saved in `calibration_images/`
calibrator = CameraCalibrator(square_size_mm=square_size_mm, board_shape=(9, 6))
camera_model = calibrator.calibrate_from_images("calibration_images/*.jpg")

# --------------------------------------------------------
# 3. Simulate pendulum trajectory
# --------------------------------------------------------

pendulum = Pendulum(L_string=0.127, R_sphere=0.013, g=9.81)
simulator = PendulumSimulator(pendulum)

# Initial conditions: [theta, phi, dtheta, dphi] in radians
init_conditions = [10 * np.pi / 180, 0, 60 * np.pi / 180, 150 * np.pi / 180]
t, states = simulator.simulate(init_conditions, t_max=5.0, num_samples=500)
x, y, z = simulator.compute_cartesian(states)

# --------------------------------------------------------
# 4. Simulate camera view of checkerboard
# --------------------------------------------------------

# Use first extrinsic parameters (for demo)
rvec = camera_model.rvecs[0]
tvec = camera_model.tvecs[0]

# Define world plane size (checkerboard physical size)
world_size_mm = (square_size_mm * 9, square_size_mm * 6)

# Simulate camera view with noise
noise_params = {"gaussian_std": 5.0, "poisson_lambda": 10.0, "motion_blur": True}
simulated_img = simulate_camera_view(
    camera_model,
    checker_img,
    world_size_mm,
    img_size_px=(480, 640),
    rvec=rvec,
    tvec=tvec,
    noise_params=noise_params,
)

# Save and show simulated image
cv2.imwrite("simulated_camera_view.png", simulated_img)
cv2.imshow("Simulated Camera View", simulated_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --------------------------------------------------------
# 5. Validate: Reprojection error and MSE (example)
# --------------------------------------------------------

# Example: compute reprojection error (if you still have object/image points from calibration)
# (Here we just show the call; objpoints/imgpoints must be saved during calibration)
# error = compute_reprojection_error(camera_model, objpoints, imgpoints)
# print(f"Mean reprojection error: {error:.3f} pixels")

# Example: compare simulated vs real captured image (must load real captured image first)
# real_img = cv2.imread("captured_view.png", cv2.IMREAD_GRAYSCALE)
# mse = compute_mse(simulated_img, real_img)
# print(f"Pixel MSE between simulated and real image: {mse:.2f}")
