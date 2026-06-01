from lib.smart_config import smart_config
from lightx2v.common.modules.weight_module import WeightModule


class NeoppPostWeights(WeightModule):
    def __init__(self, config):
        super().__init__()
        self.config = config
