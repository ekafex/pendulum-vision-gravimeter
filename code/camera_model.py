# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 20:45:00 2025

@author: ekafex

Description:
    Defines camera intrinsic/extrinsic parameters, distortion modeling,
    and calibration routines using OpenCV. Provides manual projection functions
    and utilities for forward/backward transformations.

Dependencies:
    - numpy
    - opencv-python (cv2)

Notes:
    Units: All physical units are in meters or millimeters where specified.
"""

import numpy as np
import cv2
from dataclasses import dataclass, field

# ----------------------------
# Camera Model Representation
# ----------------------------


@dataclass
class CameraModel:
    """
    Represents a calibrated camera with intrinsic parameters and distortion.

    Attributes
    ----------
    K : np.ndarray
        Intrinsic matrix (3x3).
    dist_coeffs : np.ndarray
        Distortion coefficients (k1, k2, p1, p2, k3).
    rvecs : list of np.ndarray
        Rotation vectors for each calibration image.
    tvecs : list of np.ndarray
        Translation vectors for each calibration image.
    """

    K: np.ndarray
    dist_coeffs: np.ndarray
    rvecs: list = field(default_factory=list)
    tvecs: list = field(default_factory=list)

    def project_points(
        self, object_points: np.ndarray, rvec: np.ndarray, tvec: np.ndarray
    ):
        """
        Project 3D object points to 2D image points using this camera model.

        Parameters
        ----------
        object_points : np.ndarray
            Array of shape (N, 3) representing 3D world points.
        rvec : np.ndarray
            Rotation vector (Rodrigues form).
        tvec : np.ndarray
            Translation vector.

        Returns
        -------
        image_points : np.ndarray
            Array of projected 2D points (N, 2).
        """
        image_points, _ = cv2.projectPoints(
            object_points, rvec, tvec, self.K, self.dist_coeffs
        )
        return image_points.reshape(-1, 2)

    def undistort_points(self, points_2d: np.ndarray):
        """
        Undistort 2D image points using the camera's distortion parameters.

        Parameters
        ----------
        points_2d : np.ndarray
            Distorted points (N, 2).

        Returns
        -------
        undistorted_points : np.ndarray
            Undistorted points (N, 2).
        """
        undistorted = cv2.undistortPoints(
            points_2d.reshape(-1, 1, 2), self.K, self.dist_coeffs, P=self.K
        )
        return undistorted.reshape(-1, 2)


# ----------------------------
# Camera Calibration Wrapper
# ----------------------------


class CameraCalibrator:
    """
    Handles camera calibration using chessboard patterns and OpenCV functions.

    Example
    -------
    calibrator = CameraCalibrator(square_size_mm=20, board_shape=(9,6))
    camera_model = calibrator.calibrate_from_images("images/*.jpg")
    """

    def __init__(self, square_size_mm: float, board_shape=(9, 6)):
        """
        Parameters
        ----------
        square_size_mm : float
            Physical size of one chessboard square (mm).
        board_shape : tuple of int
            Number of inner corners per chessboard row and column (cols, rows).
        """
        self.square_size_mm = square_size_mm
        self.board_shape = board_shape

    def _prepare_object_points(self):
        """
        Generate 3D world coordinates for the chessboard corners (Z=0 plane).

        Returns
        -------
        objp : np.ndarray
            Array of shape (N, 3) with 3D coordinates in mm.
        """
        cols, rows = self.board_shape
        objp = np.zeros((rows * cols, 3), np.float32)
        objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
        objp *= self.square_size_mm
        return objp

    def calibrate_from_images(self, image_glob: str):
        """
        Calibrate the camera using multiple chessboard images.

        Parameters
        ----------
        image_glob : str
            Glob pattern to load calibration images (e.g., 'images/*.jpg').

        Returns
        -------
        CameraModel
            Calibrated camera model containing K, distortion, rvecs, and tvecs.
        """
        import glob

        objp = self._prepare_object_points()
        objpoints = []  # 3D points
        imgpoints = []  # 2D points

        images = glob.glob(image_glob)
        if not images:
            raise FileNotFoundError(f"No images found for pattern: {image_glob}")

        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect corners
            ret, corners = cv2.findChessboardCorners(gray, self.board_shape, None)
            if ret:
                corners_refined = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                )
                objpoints.append(objp)
                imgpoints.append(corners_refined)

        if not objpoints:
            raise RuntimeError("No valid chessboard detections for calibration.")

        # Calibrate
        ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )

        print(f"Calibration RMS error: {ret}")
        return CameraModel(K=K, dist_coeffs=dist, rvecs=rvecs, tvecs=tvecs)
