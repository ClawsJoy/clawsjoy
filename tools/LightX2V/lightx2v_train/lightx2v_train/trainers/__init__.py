from lib.smart_config import smart_config
from lightx2v_train.utils.registry import build_trainer

from .lora import LoraTrainer

__all__ = ["build_trainer", "LoraTrainer"]
