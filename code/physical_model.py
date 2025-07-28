# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 21:15:00 2025

@author: ekafex

Description:
    Defines the physical model of a spherical pendulum with damping.
    Provides classes for parameter storage and simulation using ODE integration.

Dependencies:
    - numpy
    - scipy.integrate (solve_ivp)

Notes:
    - All physical quantities are in SI units (meters, seconds, radians).
    - Initial conditions are given as [theta, phi, dtheta, dphi].
    - The model supports light damping and gravitational effects only.
"""

import numpy as np
from dataclasses import dataclass
from scipy.integrate import solve_ivp


# --------------------------------------------------------
# Pendulum Parameters
# --------------------------------------------------------


@dataclass
class Pendulum:
    """
    Represents the physical parameters of a spherical pendulum.

    Attributes
    ----------
    L_string : float
        Length of the pendulum string (m).
    R_sphere : float
        Radius of the pendulum bob (m).
    g : float
        Gravitational acceleration (m/s^2).
    delta_theta : float
        Damping coefficient for polar motion.
    delta_phi : float
        Damping coefficient for azimuthal motion.
    """

    L_string: float = 0.127  # m
    R_sphere: float = 0.013  # m
    g: float = 9.81  # m/s^2
    delta_theta: float = 3e-3  # damping coefficient polar
    delta_phi: float = 3e-3  # damping coefficient azimuthal

    @property
    def length(self) -> float:
        """Total pendulum length (string + sphere radius)."""
        return self.L_string + self.R_sphere


# --------------------------------------------------------
# Pendulum Simulator
# --------------------------------------------------------


class PendulumSimulator:
    """
    Simulates the dynamics of a spherical pendulum using ODE integration.
    """

    def __init__(self, pendulum: Pendulum):
        self.pendulum = pendulum
        self.w0 = np.sqrt(pendulum.g / pendulum.length)

    def dynamics(self, t, state):
        """
        Compute time derivatives for spherical pendulum.

        Parameters
        ----------
        t : float
            Current time (s).
        state : ndarray
            State vector [theta, phi, dtheta, dphi].

        Returns
        -------
        dstate_dt : ndarray
            Time derivatives [dtheta, dphi, ddtheta, ddphi].
        """
        th, ph, dth, dph = state
        p = self.pendulum

        # Equations of motion (spherical coordinates)
        ddth = (
            np.sin(th) * np.cos(th) * dph**2
            - self.w0**2 * np.sin(th)
            - 2 * p.delta_theta * dth
        )
        ddph = (
            -2 * dth * dph * np.cos(th) / np.sin(th + 1e-6)
            - 2 * p.delta_phi * np.sin(th) * dph
        )

        return [dth, dph, ddth, ddph]

    def simulate(self, initial_conditions, t_max=10.0, num_samples=1000):
        """
        Simulate pendulum motion over time.

        Parameters
        ----------
        initial_conditions : list or tuple
            Initial [theta, phi, dtheta, dphi] (rad, rad, rad/s, rad/s).
        t_max : float
            Total simulation time in seconds.
        num_samples : int
            Number of output samples.

        Returns
        -------
        t : ndarray
            Time vector (s).
        states : ndarray
            Array of shape (num_samples, 4) with [theta, phi, dtheta, dphi].
        """
        t_eval = np.linspace(0, t_max, num_samples)
        sol = solve_ivp(
            self.dynamics, [0, t_max], initial_conditions, t_eval=t_eval, method="RK45"
        )
        return sol.t, sol.y.T

    def compute_cartesian(self, states):
        """
        Convert [theta, phi] states to Cartesian coordinates.

        Parameters
        ----------
        states : ndarray
            Array of shape (N, 4) with [theta, phi, dtheta, dphi].

        Returns
        -------
        x, y, z : ndarray
            Cartesian coordinates in meters.
        """
        th = states[:, 0]
        ph = states[:, 1]
        L = self.pendulum.length

        x = L * np.sin(th) * np.cos(ph)
        y = L * np.sin(th) * np.sin(ph)
        z = L * (1 - np.cos(th))

        return x, y, z

    def compute_velocity(self, states):
        """
        Compute velocity components from [theta, phi, dtheta, dphi].

        Parameters
        ----------
        states : ndarray
            Array of shape (N, 4).

        Returns
        -------
        vx, vy, vz : ndarray
            Velocity components (m/s).
        """
        th, ph, dth, dph = states[:, 0], states[:, 1], states[:, 2], states[:, 3]
        L = self.pendulum.length

        vx = L * (np.cos(th) * np.cos(ph) * dth - np.sin(th) * np.sin(ph) * dph)
        vy = L * (np.cos(th) * np.sin(ph) * dth + np.sin(th) * np.cos(ph) * dph)
        vz = L * np.sin(th) * dth

        return vx, vy, vz

    def compute_energy(self, states):
        """
        Compute kinetic and potential energy of the pendulum.

        Parameters
        ----------
        states : ndarray
            Array of shape (N, 4).

        Returns
        -------
        E_kin, E_pot, E_tot : ndarray
            Energies in Joules (assuming unit mass).
        """
        vx, vy, vz = self.compute_velocity(states)
        th = states[:, 0]
        L = self.pendulum.length
        g = self.pendulum.g

        E_kin = 0.5 * (vx**2 + vy**2 + vz**2)
        E_pot = g * L * (1 - np.cos(th))
        E_tot = E_kin + E_pot
        return E_kin, E_pot, E_tot
