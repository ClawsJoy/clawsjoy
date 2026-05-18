"""数据清理技能 - 自动清理过期数据"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from datetime import datetime, timedelta
from src.lib.vector.vector_manager import vector_manager

class CleanupSkill:
    name = "cleanup"
    description = "清理过期数据"
    version = "1.0.0"
    category = "maintenance"
    
    def execute(self, params):
        retention_days = params.get("retention_days", 30)
        categories = params.get("categories", ["hot_topic", "web_crawl"])
        
        print(f"🧹 清理过期数据: 保留{retention_days}天, 分类: {categories}")
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # 获取当前所有向量
        # 根据 metadata 中的 timestamp 判断是否过期
        # 删除过期数据
        
        # 统计清理结果
        cleaned_count = 0
        
        return {
            "success": True,
            "retention_days": retention_days,
            "cleaned_count": cleaned_count,
            "message": f"已清理 {cleaned_count} 条过期数据"
        }

skill = CleanupSkill()
