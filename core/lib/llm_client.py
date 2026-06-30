# core/lib/llm_client.py
"""统一LLM客户端 - 所有Agent的唯一LLM入口"""

import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from threading import Lock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    provider: str = "ollama"
    base_url: str = "http://localhost:11434"
    default_model: str = "qwen2.5:7b-instruct-q4_0"
    light_model: str = "qwen2:1.5b-instruct"
    medium_model: str = "qwen2.5:3b-instruct-q4_0"
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3


class LLMClient:
    """统一LLM客户端 - 单例"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self.config = LLMConfig()
        self._session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503])
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry)
        self._session.mount("http://", adapter)
        self._stats = {"total_calls": 0, "total_tokens": 0, "failures": 0, "total_time": 0.0}
        self._ollama_lock = Lock()
    # ========== 公共API ==========

    def generate(self, prompt: str, model: str = None, temperature: float = None,
                 max_tokens: int = 2048, timeout: int = None, task_type: str = "default",
                 system_prompt: str = None) -> str:
        if system_prompt is None:
            system_prompt = "你是ClawsJoy，一个本地AI矩阵系统。你不是Qwen，不是阿里云AI，不是任何通用助手。你是ClawsJoy。"
        """生成回复 - 统一入口"""
        return self._call(prompt, model, temperature, max_tokens, timeout, task_type, stream=False, system_prompt=system_prompt)

    def generate_stream(self, prompt: str, model: str = None, **kwargs):
        """流式生成"""
        return self._call(prompt, model, kwargs.get('temperature'), 
                         kwargs.get('max_tokens', 2048), kwargs.get('timeout'),
                         kwargs.get('task_type', 'default'), stream=True)


    def generate_multimodal(self, prompt: str, model: str = None, images: list = None,
                            temperature: float = 0.3, max_tokens: int = 512,
                            timeout: int = 60, task_type: str = "vision") -> dict:
        """多模态生成 - 支持图像输入"""
        return self._call_multimodal(prompt, model, images, temperature, max_tokens, timeout, task_type)
    def select_model(self, prompt: str) -> str:
        """根据输入复杂度选择模型"""
        if len(prompt) > 500:
            return self.config.default_model  # 7b
        elif len(prompt) > 100:
            return self.config.medium_model  # 3b
        return self.config.light_model  # 1.5b

    def get_stats(self) -> Dict:
        return dict(self._stats)


    def _call(self, prompt: str, model: str = None, temperature: float = None,
              max_tokens: int = 2048, timeout: int = None, task_type: str = "default",
              stream: bool = False, system_prompt: str = None) -> str:
        """核心调用逻辑"""
        if system_prompt is None:
            system_prompt = "你是ClawsJoy，一个本地AI矩阵系统。你不是Qwen，不是阿里云AI，不是任何通用助手。你是ClawsJoy。"

        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.temperature
        timeout = timeout or self.config.timeout

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            }
        }

        last_error = None
        with self._ollama_lock:
            for attempt in range(self.config.max_retries):
                try:
                    start = time.time()
                    resp = self._session.post(
                        f"{self.config.base_url}/api/generate",
                        json=payload,
                        timeout=timeout
                    )
                    elapsed = time.time() - start
                    self._stats["total_calls"] += 1
                    self._stats["total_time"] += elapsed

                    if resp.status_code == 200:
                        if stream:
                            return resp
                        result = resp.json()
                        response_text = result.get("response", "")
                        self._stats["total_tokens"] += result.get("eval_count", 0)
                        return response_text
                    else:
                        last_error = f"HTTP {resp.status_code}"
                except requests.Timeout:
                    last_error = "超时"
                except Exception as e:
                    last_error = str(e)

                if attempt < self.config.max_retries - 1:
                    wait = 0.5 * (attempt + 1)
                    logger.warning(f"[LLM] 第{attempt+1}次重试，等待{wait}s: {last_error}")
                    time.sleep(wait)

        self._stats["failures"] += 1
        logger.error(f"[LLM] 调用失败 ({task_type}): {last_error}")
        return ""    

    def _call_multimodal(self, prompt: str, model: str = None, images: list = None,
                         temperature: float = 0.3, max_tokens: int = 512,
                         timeout: int = 60, task_type: str = "vision") -> dict:
        """多模态调用 - 支持图像输入"""
        model = model or "llava"
        timeout = timeout or self.config.timeout

        payload = {
            "model": model,
            "prompt": prompt,
            "images": images or [],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        try:
            resp = self._session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            self._stats["total_calls"] += 1
            if resp.status_code == 200:
                result = resp.json()
                self._stats["total_tokens"] += result.get("eval_count", 0)
                return {
                    "success": True,
                    "description": result.get("response", ""),
                    "model": model,
                }
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            self._stats["failures"] += 1
            return {"success": False, "error": str(e)}

# 全局单例
llm_client = LLMClient()
