"""
helper.py

This file contains helper functions that can be reused
throughout the project.
"""

from datetime import datetime


def get_current_timestamp():
    """
    Returns the current date and time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")