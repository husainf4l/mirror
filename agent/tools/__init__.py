"""
Agent Tools Package

This package contains tools that the LiveKit agent can use to interact with the mirror system.
"""

from .agent_functions import (
    update_display,
    start_session,
    close_session,
    reset_for_next_guest,
    stop_recording_session,
)

__all__ = [
    'update_display',
    'start_session',
    'close_session',
    'reset_for_next_guest',
    'stop_recording_session',
]