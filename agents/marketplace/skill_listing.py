"""用户技能链上架系统"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SkillListing:
    """用户技能上架申请"""
    
    def __init__(self):
        self.listings_dir = Path("data/skill_listings")
        self.listings_dir.mkdir(parents=True, exist_ok=True)
    
    def submit_listing(self, user_id: str, skill_chain: Dict, brain_stats: Dict) -> Dict:
        """提交上架申请"""
        import uuid
        listing_id = str(uuid.uuid4())[:8]
        
        # 计算成熟度分数
        maturity_score = self._calculate_maturity(brain_stats)
        
        listing = {
            'id': listing_id,
            'user_id': user_id,
            'skill_chain': skill_chain,
            'brain_stats': brain_stats,
            'maturity_score': maturity_score,
            'status': 'pending',  # pending, approved, rejected
            'submitted_at': datetime.now().isoformat(),
            'approved_at': None,
            'sales_count': 0,
            'rating': 0
        }
        
        with open(self.listings_dir / f"{listing_id}.json", 'w') as f:
            json.dump(listing, f, indent=2)
        
        return {'listing_id': listing_id, 'maturity_score': maturity_score}
    
    def _calculate_maturity(self, brain_stats: Dict) -> float:
        """计算技能成熟度 (0-100)"""
        # 基于大脑经验、成功率、使用次数
        total_exp = brain_stats.get('total_experiences', 0)
        success_rate = brain_stats.get('success_rate', 0)
        
        # 经验分 (0-50)
        exp_score = min(50, total_exp / 2)
        # 成功率分 (0-50)
        success_score = success_rate * 50
        
        return min(100, exp_score + success_score)
    
    def get_pending_listings(self) -> List[Dict]:
        """获取待审核列表（管理员）"""
        listings = []
        for f in self.listings_dir.glob("*.json"):
            with open(f, 'r') as file:
                listing = json.load(file)
                if listing['status'] == 'pending':
                    listings.append(listing)
        return listings
    
    def approve_listing(self, listing_id: str) -> Dict:
        """批准上架（管理员）"""
        listing_file = self.listings_dir / f"{listing_id}.json"
        if not listing_file.exists():
            return {'error': 'Listing not found'}
        
        with open(listing_file, 'r') as f:
            listing = json.load(f)
        
        listing['status'] = 'approved'
        listing['approved_at'] = datetime.now().isoformat()
        
        # 添加到商品目录
        self._add_to_marketplace(listing)
        
        with open(listing_file, 'w') as f:
            json.dump(listing, f, indent=2)
        
        return {'success': True, 'message': 'Skill approved and listed'}
    
    def _add_to_marketplace(self, listing: Dict):
        """添加到商品商店"""
        marketplace_dir = Path("marketplace/user_skills")
        marketplace_dir.mkdir(parents=True, exist_ok=True)
        
        skill_chain = listing['skill_chain']
        manifest = {
            'name': skill_chain.get('name', f"user_skill_{listing['id']}"),
            'description': skill_chain.get('description', '用户创建的技能链'),
            'category': 'user_created',
            'price': 0.99,
            'author': listing['user_id'],
            'maturity_score': listing['maturity_score'],
            'version': '1.0.0',
            'created_at': listing['submitted_at']
        }
        
        with open(marketplace_dir / f"{listing['id']}.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ 已添加到商店: {manifest['name']}")

skill_listing = SkillListing()
