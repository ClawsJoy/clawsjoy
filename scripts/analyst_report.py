#!/usr/bin/env python3
"""ClawsJoy 分析师完整报告"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import json
from datetime import datetime
from intelligence.unified_analyzer import UnifiedAnalyzer
from intelligence.advanced_analyzer import AdvancedAnalyzer
from intelligence.predictor import IntelligentPredictor

def generate_full_report():
    print("=" * 60)
    print(f"ClawsJoy 分析师报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 统一分析
    print("\n📊 1. 系统分析")
    unified = UnifiedAnalyzer()
    result = unified.analyze()
    print(f"   评估: {result.get('summary', 'N/A')}")
    issues = result.get('critical_issues', [])
    if issues:
        print(f"   关键问题:")
        for issue in issues[:3]:
            print(f"     - {issue[:60]}...")
    
    # 2. 趋势分析
    print("\n📈 2. 趋势分析")
    advanced = AdvancedAnalyzer()
    trend = advanced.get_trend()
    print(f"   趋势: {trend.get('trend', 'N/A')}")
    print(f"   置信度: {trend.get('confidence', 0)}")
    
    # 3. 根因分析
    print("\n🔍 3. 根因分析")
    root_cause = advanced.root_cause_analysis()
    if root_cause.get('root_causes'):
        print(f"   根本原因:")
        for cause in root_cause['root_causes'][:2]:
            print(f"     - {cause}")
    
    # 4. 预测
    print("\n🔮 4. 智能预测")
    predictor = IntelligentPredictor()
    predictor.record_metric('success_rate', 34.4)
    try:
        forecast = predictor.generate_forecast(days=7)
        print(f"   7天预测: {forecast}")
    except:
        print("   预测数据不足")
    
    print("\n" + "=" * 60)
    print("✅ 报告生成完成")

if __name__ == "__main__":
    generate_full_report()
