from dataclasses import dataclass

import torch
from lightx2v.models.networks.seedvr.utils.cache import Cache

from lib.smart_config import smart_config


@dataclass
class SeedVRPreInferOutput:
    vid: torch.Tensor
    txt: torch.Tensor
    vid_shape: torch.LongTensor
    txt_shape: torch.LongTensor
    emb: torch.Tensor
    cache: Cache
