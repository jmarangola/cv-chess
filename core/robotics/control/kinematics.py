"""
    Forward and inverse kinematics computations for robot joint control 
    John Marangola - marangol@bc.edu
"""

from robot_parameters import A1, A2
import numpy as np
import math

def get_theta_two(x, y):
    """
    Get theta2 angle for robot arm given (x, y) world position

    Args:
        x (double): end effector x position
        y (double): end effector y position

    Returns:
        double: theta2 value (in radians)
    """
    x_sq = math.pow(x, 2)
    y_sq = math.pow(y, 2)
    return np.arccos((x_sq + y_sq - math.pow(A1, 2) - math.pow(A2, 2))/(2 * A1 * A2))

def get_theta_one(x, y, thet2):
    """
    Get theta1 angle of robot arm for a given (x, y, theta2) configuration (theta2 must be pre-computed).

    Args:
        x (double): end effector x position
        y (double): end effector y position
        thet2 (double): theta2 position defined relative to theta 1 (in radians)

    Returns:
        double: theta1 position (in radians)
    """
    tx = A2*np.sin(thet2)*x + (A1 + A2 * np.cos(thet2)*y)
    ty = (A1 + A2 * np.cos(thet2)) * x - A2 * np.sin(thet2) * y
    return np.arctan2(tx, ty)

def inv_theta(pos):
    """
    Inverse kinematic computation of (theta1, theta2) from (x, y) world position

    Args:
        pos (list): List of end effector position doubles [x, y]

    Returns:
        list: List of joint positions [theta1, theta2]
    """
    x, y = pos[0], pos[1]
    thet2 = get_theta_two(x, y)
    return (get_theta_one(x, y, thet2), thet2)

