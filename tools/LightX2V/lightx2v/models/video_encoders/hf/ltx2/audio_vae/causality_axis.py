from lib.smart_config import smart_config
from enum import Enum


class CausalityAxis(Enum):
    """Enum for specifying the causality axis in causal convolutions."""

    NONE = None
    WIDTH = "width"
    HEIGHT = "height"
    WIDTH_COMPATIBILITY = "width-compatibility"
