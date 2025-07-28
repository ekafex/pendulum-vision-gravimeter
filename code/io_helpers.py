# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 22:40:00 2025

@author: ekafex

Description:
    Provides helper functions to save and load camera calibration data
    (intrinsic matrix, distortion coefficients, extrinsic parameters)
    to/from YAML files using OpenCV's FileStorage.

Dependencies:
    - numpy
    - opencv-python

Usage:
    from camera_simulation.io_helpers import save_calibration, load_calibration

    # Save
    save_calibration("calibration.yaml", camera_model)

    # Load
    loaded_camera_model = load_calibration("calibration.yaml")
"""

import cv2
import numpy as np
from camera_model import CameraModel


def save_calibration(filename: str, camera_model: CameraModel):
    """
    Save camera calibration data to a YAML file.

    Parameters
    ----------
    filename : str
        Path to output YAML file.
    camera_model : CameraModel
        Camera model containing intrinsics, distortion, and extrinsics.
    """
    fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
    fs.write("K", camera_model.K)
    fs.write("dist_coeffs", camera_model.dist_coeffs)

    # Save extrinsics if available
    if camera_model.rvecs and camera_model.tvecs:
        rvecs = np.array(camera_model.rvecs, dtype=np.float32)
        tvecs = np.array(camera_model.tvecs, dtype=np.float32)
        fs.write("rvecs", rvecs)
        fs.write("tvecs", tvecs)

    fs.release()


def load_calibration(filename: str) -> CameraModel:
    """
    Load camera calibration data from a YAML file.

    Parameters
    ----------
    filename : str
        Path to input YAML file.

    Returns
    -------
    CameraModel
        Camera model reconstructed from the file.
    """
    fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)

    K = fs.getNode("K").mat()
    dist = fs.getNode("dist_coeffs").mat()

    rvecs_node = fs.getNode("rvecs")
    tvecs_node = fs.getNode("tvecs")

    rvecs = []
    tvecs = []
    if not rvecs_node.empty():
        rvecs = [rv.reshape(3, 1) for rv in rvecs_node.mat()]
    if not tvecs_node.empty():
        tvecs = [tv.reshape(3, 1) for tv in tvecs_node.mat()]

    fs.release()

    return CameraModel(K=K, dist_coeffs=dist, rvecs=rvecs, tvecs=tvecs)
