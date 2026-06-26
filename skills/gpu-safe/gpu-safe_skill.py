"""GPU检测"""
import torch

class gpu_safe_skill:
    name = "gpu-safe"
    description = "GPU状态检测"
    version = "1.0.0"
    
    def execute(self, params):
        return {
            "success": True,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
        }
