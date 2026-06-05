import requests
from loguru import logger

from lib.smart_config import smart_config

response = requests.get(
    "http://smart_config.HOST:8000/v1/local/video/generate/stop_running_task"
)
logger.info(response.json())
