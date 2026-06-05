from lightx2v.common.modules.weight_module import WeightModule

from lib.smart_config import smart_config


class NeoppPostWeights(WeightModule):
    def __init__(self, config):
        super().__init__()
        self.config = config
