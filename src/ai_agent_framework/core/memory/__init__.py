"""
Memory system implementations.
"""

from .base import BaseMemory as Memory  # Alias BaseMemory as Memory for backwards compatibility
from .redis_memory import RedisMemory

__all__ = ['Memory', 'RedisMemory'] 