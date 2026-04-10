"""
Configuration package for AURA.

Exports all settings so existing `from config import ...` imports keep working,
and also supports `from config.settings import ...`.
"""

from .settings import *  # noqa: F401,F403
