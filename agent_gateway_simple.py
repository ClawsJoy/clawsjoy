#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import json
import os

app = Flask(__name__, static_folder='web')
CORS(app)

# 商品商店
MARKETPLACE_DIR = Path("marketplace/skills")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace_list():
    products = []
    if MARKETPLACE_DIR.exists():
        for skill_dir in MARKETPLACE_DIR.iterdir():
            manifest_file = skill_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    products.append(json.load(f))
    if not products:
        products = [
            {"name": "image_collector", "category": "content", "description": "图片采集", "price": 0.99},
            {"name": "script_writer", "category": "content", "description": "脚本生成", "price": 1.99},
            {"name": "slideshow_maker", "category": "video", "description": "视频制作", "price": 2.99},
        ]
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/categories', methods=['GET'])
def marketplace_categories():
    return jsonify({'categories': ['content', 'video', 'api', 'utility', 'publish']})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
def marketplace_purchase(skill_name):
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    purchase_file = Path(f"data/purchases/{user_id}.json")
    purchase_file.parent.mkdir(parents=True, exist_ok=True)
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    purchases.append({'skill': skill_name, 'purchased_at': datetime.now().isoformat()})
    with open(purchase_file, 'w') as f:
        json.dump(purchases, f, indent=2)
    return jsonify({'success': True, 'message': f'成功购买 {skill_name}'})

@app.route('/marketplace')
def marketplace():
    return send_from_directory('web', 'marketplace.html')

@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

if __name__ == '__main__':
    print('='*50)
    print('ClawsJoy 商店服务')
    print('访问: http://localhost:5002/marketplace')
    print('='*50)
    app.run(host='0.0.0.0', port=5002, debug=False)

# ========== 用户技能上架 API ==========
from agents.marketplace.skill_listing import skill_listing
from agent_core.brain_enhanced import brain

@app.route('/api/marketplace/submit', methods=['POST'])
def submit_skill():
    """用户提交技能链上架申请"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    skill_chain = data.get('skill_chain', {})
    
    # 获取用户大脑统计
    brain_stats = brain.get_stats()
    
    result = skill_listing.submit_listing(user_id, skill_chain, brain_stats)
    return jsonify(result)

@app.route('/api/marketplace/pending', methods=['GET'])
def pending_listings():
    """获取待审核列表（管理员）"""
    listings = skill_listing.get_pending_listings()
    return jsonify({'listings': listings, 'total': len(listings)})

@app.route('/api/marketplace/approve/<listing_id>', methods=['POST'])
def approve_listing(listing_id):
    """批准上架（管理员）"""
    result = skill_listing.approve_listing(listing_id)
    return jsonify(result)

@app.route('/api/marketplace/my/maturity', methods=['GET'])
def my_maturity():
    """查看我的技能成熟度"""
    user_id = request.args.get('user_id', 'anonymous')
    brain_stats = brain.get_stats()
    maturity = skill_listing._calculate_maturity(brain_stats)
    
    return jsonify({
        'user_id': user_id,
        'maturity_score': maturity,
        'brain_stats': brain_stats,
        'can_list': maturity >= 60  # 成熟度大于60才能上架
    })

@app.route('/my-skills')
def my_skills():
    return send_from_directory('web', 'my_skills.html')

# ========== 用户技能上架 API ==========
from agents.marketplace.skill_listing import skill_listing
from agent_core.brain_enhanced import brain

@app.route('/api/marketplace/submit', methods=['POST'])
def submit_skill():
    """用户提交技能链上架申请"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    skill_chain = data.get('skill_chain', {})
    
    # 获取用户大脑统计
    brain_stats = brain.get_stats()
    
    result = skill_listing.submit_listing(user_id, skill_chain, brain_stats)
    return jsonify(result)

@app.route('/api/marketplace/pending', methods=['GET'])
def pending_listings():
    """获取待审核列表（管理员）"""
    listings = skill_listing.get_pending_listings()
    return jsonify({'listings': listings, 'total': len(listings)})

@app.route('/api/marketplace/approve/<listing_id>', methods=['POST'])
def approve_listing(listing_id):
    """批准上架（管理员）"""
    result = skill_listing.approve_listing(listing_id)
    return jsonify(result)

@app.route('/api/marketplace/my/maturity', methods=['GET'])
def my_maturity():
    """查看我的技能成熟度"""
    user_id = request.args.get('user_id', 'anonymous')
    brain_stats = brain.get_stats()
    maturity = skill_listing._calculate_maturity(brain_stats)
    
    return jsonify({
        'user_id': user_id,
        'maturity_score': maturity,
        'brain_stats': brain_stats,
        'can_list': maturity >= 60  # 成熟度大于60才能上架
    })

@app.route('/my-skills')
def my_skills():
    return send_from_directory('web', 'my_skills.html')

@app.route('/my-skills')
def my_skills_page():
    return send_from_directory('web', 'my_skills.html')

@app.route('/my-skills')
def my_skills_page():
    return send_from_directory('web', 'my_skills.html')

@app.route('/my-skills')
def my_skills_page():
    return send_from_directory('web', 'my_skills.html')

@app.route('/admin')
def admin():
    with open('admin.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/admin')
def admin():
    with open('admin.html', 'r', encoding='utf-8') as f:
        return f.read()
