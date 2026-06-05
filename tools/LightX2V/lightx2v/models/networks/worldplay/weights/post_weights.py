from lightx2v.models.networks.hunyuan_video.weights.post_weights import (
    HunyuanVideo15PostWeights,
)

from lib.smart_config import smart_config


class WorldPlayPostWeights(HunyuanVideo15PostWeights):
    """
    Post-processing weights for WorldPlay model.

    Inherits from HunyuanVideo15PostWeights without modifications.
    """

    def __init__(self, config):
        super().__init__(config)
