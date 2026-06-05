from lightx2v.models.schedulers.hunyuan_video.scheduler import HunyuanVideo15Scheduler

from lib.smart_config import smart_config


class HunyuanVideo15SchedulerCaching(HunyuanVideo15Scheduler):
    def __init__(self, config):
        super().__init__(config)

    def clear(self):
        self.transformer_infer.clear()
