import json
from lib.memory_simple import memory

class DataContract:
    @staticmethod
    def store_analysis(data):
        memory.remember(json.dumps(data, ensure_ascii=False), category='system_analysis')
    
    @staticmethod
    def get_latest_analysis():
        items = memory.recall_all(category='system_analysis')
        for item in reversed(items):
            try:
                return json.loads(item)
            except:
                continue
        return None
    
    @staticmethod
    def store_design(designs):
        # 直接存储，不包装
        memory.remember(json.dumps(designs, ensure_ascii=False), category='fix_designs')
        print(f'[DataContract] 已存储 {len(designs)} 个设计方案')
    
    @staticmethod
    def get_latest_design():
        items = memory.recall_all(category='fix_designs')
        for item in reversed(items):
            try:
                return json.loads(item)
            except:
                continue
        return None
