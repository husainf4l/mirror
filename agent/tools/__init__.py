"""
Agent Tools Package

This package contains tools that the LiveKit agent can use to interact with the mirror system.
"""

from .agent_functions import (
    get_guest_about,
    get_guest_info,
    update_mirror_with_guest_info,
    update_mirror_display,
    play_mirror_audio,
    close_session,
)

__all__ = [
    'get_guest_about',
    'get_guest_info',
    'update_mirror_with_guest_info',
    'update_mirror_display',
    'play_mirror_audio',
    'close_session',
]