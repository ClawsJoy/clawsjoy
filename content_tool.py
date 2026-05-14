#!/usr/bin/env python3
"""内容生产管理 - 简单可用"""
import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/content_projects.json")

def init():
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def list_projects():
    with open(DATA_FILE, 'r') as f:
        projects = json.load(f)
    
    if not projects:
        print("暂无项目")
        return
    
    print("\n" + "="*60)
    print("📋 内容项目列表")
    print("="*60)
    
    for p in projects:
        status = "✅" if p.get('score', 0) >= 7 else "⏳"
        print(f"{status} [{p['id']}] {p['title']}")
        print(f"   阶段: {p['stage']} | 评分: {p.get('score', '未审')}")
        print(f"   创建: {p['created_at'][:16]}")
        print()

def create_project():
    title = input("项目标题: ").strip()
    source = input("素材来源/URL: ").strip()
    
    with open(DATA_FILE, 'r') as f:
        projects = json.load(f)
    
    new_id = max([p['id'] for p in projects], default=0) + 1
    
    projects.append({
        'id': new_id,
        'title': title,
        'source': source,
        'stage': 'collect',
        'score': None,
        'feedback': '',
        'created_at': datetime.now().isoformat(),
        'history': []
    })
    
    with open(DATA_FILE, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"\n✅ 项目创建成功! ID: {new_id}")

def review_project():
    list_projects()
    pid = int(input("\n输入项目ID: "))
    
    with open(DATA_FILE, 'r') as f:
        projects = json.load(f)
    
    for p in projects:
        if p['id'] == pid:
            print(f"\n📄 {p['title']}")
            print(f"素材: {p['source']}")
            print(f"当前阶段: {p['stage']}")
            
            score = int(input("评分 (1-10): "))
            feedback = input("反馈意见: ")
            
            p['score'] = score
            p['feedback'] = feedback
            p['stage'] = 'reviewed' if score >= 7 else 'rework'
            p['reviewed_at'] = datetime.now().isoformat()
            p['history'].append({
                'action': 'review',
                'score': score,
                'feedback': feedback,
                'time': datetime.now().isoformat()
            })
            
            with open(DATA_FILE, 'w') as f:
                json.dump(projects, f, indent=2)
            
            print(f"\n✅ 已记录评分: {score}/10")
            print(f"项目状态: {'通过✅' if score >= 7 else '需修改🔧'}")
            return
    
    print("项目不存在")

def dashboard():
    with open(DATA_FILE, 'r') as f:
        projects = json.load(f)
    
    print("\n" + "="*60)
    print("📊 审核看板")
    print("="*60)
    
    pending = [p for p in projects if p.get('score') is None]
    approved = [p for p in projects if p.get('score', 0) >= 7]
    rejected = [p for p in projects if p.get('score', 0) < 7 and p.get('score') is not None]
    
    print(f"\n⏳ 待审核: {len(pending)}")
    for p in pending[:5]:
        print(f"   [{p['id']}] {p['title']}")
    
    print(f"\n✅ 已通过: {len(approved)}")
    for p in approved[:5]:
        print(f"   [{p['id']}] {p['title']} (评分: {p['score']})")
    
    print(f"\n🔧 需修改: {len(rejected)}")
    
    print("\n" + "="*60)

def main():
    init()
    
    while True:
        print("\n" + "="*40)
        print("内容管理工具")
        print("1. 查看看板")
        print("2. 创建项目")
        print("3. 项目列表")
        print("4. 审核评分")
        print("5. 退出")
        print("="*40)
        
        choice = input("选择: ").strip()
        
        if choice == '1':
            dashboard()
        elif choice == '2':
            create_project()
        elif choice == '3':
            list_projects()
        elif choice == '4':
            review_project()
        elif choice == '5':
            break

if __name__ == "__main__":
    main()
