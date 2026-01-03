"""
Embryonic Story System
Biological-inspired parametric cascade with evolutionary learning
"""

from .core import (
    LearningEmbryo,
    LearningCell,
    LearningParameters,
    StoryEvolutionEngine,
    PerformanceMetrics,
)
from .storage import EmbryoStorage
from .assets import AssetLibrary

__version__ = "0.1.0"
__all__ = [
    "LearningEmbryo",
    "LearningCell",
    "LearningParameters",
    "StoryEvolutionEngine",
    "PerformanceMetrics",
    "EmbryoStorage",
    "AssetLibrary",
]
