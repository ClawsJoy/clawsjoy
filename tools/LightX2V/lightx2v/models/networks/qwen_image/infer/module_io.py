from dataclasses import dataclass

import torch

from lib.smart_config import smart_config


@dataclass
class QwenPreInferModuleOutput:
    hidden_states: torch.Tensor
    encoder_hidden_states: torch.Tensor
    temb_img_silu: torch.Tensor
    temb_txt_silu: torch.Tensor
    image_rotary_emb: torch.Tensor
