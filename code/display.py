# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 21:05:00 2025

@author: ekafex

Description:
    This module defines the `Display` class, which models a physical display
    (monitor or screen) by storing its pixel dimensions and physical size.
    It provides tools for converting between pixel and physical coordinates
    (mm), and for generating accurate calibration patterns such as checkerboards.

Dependencies:
    - numpy
    - matplotlib

Notes:
    - All physical dimensions are in meters internally, with conversion functions
      provided to return values in millimeters.
    - Designed for calibration workflows where the exact physical scaling of
      displayed patterns is critical (e.g., camera calibration with on-screen targets).
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class Display:
    """
    Represents a physical display (monitor or screen) with known pixel density.

    Attributes
    ----------
    width_m : float
        Physical width of the screen in meters.
    height_m : float
        Physical height of the screen in meters.
    width_px : int
        Horizontal resolution of the display (pixels).
    height_px : int
        Vertical resolution of the display (pixels).
    """

    width_m: float
    height_m: float
    width_px: int
    height_px: int

    def __post_init__(self):
        # Pixel pitch in meters (center-to-center distance of pixels)
        self.pixel_pitch_x = self.width_m / self.width_px
        self.pixel_pitch_y = self.height_m / self.height_px
        # DPI values
        self.dpi_x = self.width_px / (self.width_m / 0.0254)  # 1 inch = 0.0254 m
        self.dpi_y = self.height_px / (self.height_m / 0.0254)

    def pixel_to_world(self, px_x: float, px_y: float):
        """
        Convert pixel coordinates (on screen) to physical coordinates in mm.
        Origin is top-left corner of screen.

        Parameters
        ----------
        px_x : float
            Horizontal pixel coordinate.
        px_y : float
            Vertical pixel coordinate.

        Returns
        -------
        (float, float)
            Physical coordinates (X_mm, Y_mm) in millimeters.
        """
        X_mm = px_x * self.pixel_pitch_x * 1000
        Y_mm = px_y * self.pixel_pitch_y * 1000
        return X_mm, Y_mm

    def world_to_pixel(self, X_mm: float, Y_mm: float):
        """
        Convert physical coordinates in mm to pixel coordinates on screen.

        Parameters
        ----------
        X_mm : float
            Horizontal position in mm.
        Y_mm : float
            Vertical position in mm.

        Returns
        -------
        (float, float)
            Pixel coordinates (px_x, px_y).
        """
        px_x = X_mm / (self.pixel_pitch_x * 1000)
        px_y = Y_mm / (self.pixel_pitch_y * 1000)
        return px_x, px_y


def generate_checkerboard(
    display: Display, squares=(9, 6), square_size_mm=None, invert=False
):
    """
    Generate a checkerboard pattern scaled to the physical dimensions of the display.

    Parameters
    ----------
    display : Display
        The display object containing physical and pixel properties.
    squares : tuple of int
        Number of inner squares (columns, rows).
    square_size_mm : float, optional
        Physical size of one square in millimeters. If None, the largest square size
        that fits the display is chosen automatically.
    invert : bool
        Invert colors (black-white vs white-black).

    Returns
    -------
    img : 2D numpy array
        Checkerboard image (0 and 1 values).
    square_size_mm : float
        The physical size of each square in mm.
    """
    cols, rows = squares

    # Determine square size in pixels
    if square_size_mm is None:
        # Fit maximum squares on screen
        square_size_px_x = display.width_px / (cols + 1)
        square_size_px_y = display.height_px / (rows + 1)
        square_size_px = min(square_size_px_x, square_size_px_y)
        square_size_mm = square_size_px * display.pixel_pitch_x * 1000
    else:
        square_size_px = square_size_mm / (display.pixel_pitch_x * 1000)

    # Total image size
    img_width_px = int(square_size_px * cols)
    img_height_px = int(square_size_px * rows)

    # Generate checkerboard
    pattern = np.indices((rows, cols)).sum(axis=0) % 2
    if invert:
        pattern = 1 - pattern

    img = np.kron(pattern, np.ones((int(square_size_px), int(square_size_px))))

    # Resize/crop to desired resolution (fit display center if needed)
    img = img[:img_height_px, :img_width_px]

    return img, square_size_mm


def show_checkerboard(img: np.ndarray, display: Display):
    """
    Display the checkerboard image using Matplotlib with correct physical scaling.

    Parameters
    ----------
    img : numpy.ndarray
        Checkerboard image (0 and 1 values).
    display : Display
        Display object (used to set correct figure size).
    """
    fig_width_in = img.shape[1] / display.dpi_x
    fig_height_in = img.shape[0] / display.dpi_y

    fig = plt.figure(figsize=(fig_width_in, fig_height_in), dpi=display.dpi_x)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, cmap="gray", interpolation="nearest")
    ax.axis("off")
    plt.show()
