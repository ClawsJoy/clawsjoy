#!/usr/bin/env python3
"""统一数据源分析器 - 配置驱动版"""

import sys
import json
import yaml
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.smart_config import smart_config
from lib.memory_simple import memory
from lib.llm_config import llm_config


class UnifiedAnalyzer:
    """统一分析器 - 配置驱动"""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.ollama_url = llm_config.get_ollama_url()
        self._load_config()
        self.data_sources = {}
    
    def _load_config(self):
        """加载配置"""
        config_file = Path("config/driver/analyzer.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "data_sources": [
                    {"category": "workflow_outcome", "description": "任务执行结果", "enabled": True, "weight": 0.3},
                    {"category": "error_knowledge", "description": "错误修复知识库", "enabled": True, "weight": 0.2},
                ],
                "llm": {"model": "qwen2.5:7b", "temperature": 0.3, "max_tokens": 2000},
                "analysis": {"max_samples_per_source": 5, "enable_llm_summary": True}
            }
    
    def collect_all_data(self) -> Dict:
        """收集所有数据源"""
        sources = self.config.get("data_sources", [])
        max_samples = self.config.get("analysis", {}).get("max_samples_per_source", 5)
        
        for source in sources:
            if not source.get("enabled", True):
                continue
            
            category = source.get("category")
            desc = source.get("description", category)
            
            try:
                items = memory.recall_all(category=category) if category else []
                self.data_sources[category] = {
                    'desc': desc,
                    'count': len(items),
                    'weight': source.get("weight", 0.1),
                    'samples': items[-max_samples:] if items else []
                }
            except Exception as e:
                self.data_sources[category] = {
                    'desc': desc,
                    'count': 0,
                    'weight': source.get("weight", 0.1),
                    'samples': [],
                    'error': str(e)
                }
        
        return self.data_sources
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM 进行分析"""
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.config.get("llm", {}).get("model", "qwen2.5:7b"),
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.get("llm", {}).get("temperature", 0.3),
                        "num_predict": self.config.get("llm", {}).get("max_tokens", 2000)
                    }
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
        except Exception as e:
            print(f"LLM 调用失败: {e}")
        return ""
    
    def analyze(self) -> Dict:
        """综合分析"""
        self.collect_all_data()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": self.VERSION,
            "data_sources": {},
            "summary": {},
            "suggestions": []
        }
        
        total_weight = 0
        total_score = 0
        
        for cat, data in self.data_sources.items():
            report["data_sources"][cat] = {
                "description": data.get('desc'),
                "count": data.get('count'),
                "weight": data.get('weight'),
                "has_data": data.get('count', 0) > 0
            }
            total_weight += data.get('weight', 0)
            score = min(100, data.get('count', 0) * 10) if data.get('count', 0) > 0 else 0
            total_score += score * data.get('weight', 0)
        
        report["summary"]["health_score"] = int(total_score / total_weight) if total_weight > 0 else 0
        report["summary"]["total_records"] = sum(d.get('count', 0) for d in self.data_sources.values())
        report["summary"]["active_sources"] = sum(1 for d in self.data_sources.values() if d.get('count', 0) > 0)
        
        # 生成建议
        if report["summary"]["health_score"] < 50:
            report["suggestions"].append({
                "level": "critical",
                "message": "系统健康度较低，建议检查错误知识库和任务执行情况"
            })
        elif report["summary"]["health_score"] < 70:
            report["suggestions"].append({
                "level": "warning",
                "message": "系统健康度中等，建议关注错误率和成功率"
            })
        else:
            report["suggestions"].append({
                "level": "info",
                "message": "系统运行良好，继续保持"
            })
        
        # LLM 深度分析
        if self.config.get("analysis", {}).get("enable_llm_summary", True):
            prompt = f"""根据以下数据分析系统状态，给出3条具体建议：

数据源统计:
{json.dumps(report['data_sources'], indent=2, ensure_ascii=False)}

健康度: {report['summary']['health_score']}/100

请返回 JSON 格式: {{"insights": ["建议1", "建议2", "建议3"]}}"""
            
            llm_response = self._call_llm(prompt)
            try:
                if llm_response:
                    import re
                    json_match = re.search(r'\{[^{}]*\}', llm_response)
                    if json_match:
                        insights = json.loads(json_match.group())
                        report["llm_insights"] = insights.get("insights", [])
            except:
                pass
        
        return report


if __name__ == "__main__":
    analyzer = UnifiedAnalyzer()
    result = analyzer.analyze()
    print(f"分析结果: 健康度 {result['summary']['health_score']}/100")
    print(f"数据源: {result['summary']['active_sources']}/{len(result['data_sources'])}")
    for s in result.get('suggestions', []):
        print(f"  - {s['message']}")
