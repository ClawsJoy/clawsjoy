from dataclasses import dataclass
"""Agent/技能商品化商店"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class ProductType(Enum):
    AGENT = "agent"
    SKILL = "skill"
    TOOL = "tool"
    TEMPLATE = "template"

class PricingModel(Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"

@dataclass
class Product:
    id: str
    name: str
    description: str
    type: ProductType
    pricing: PricingModel
    price: float
    author: str
    version: str
    downloads: int = 0
    rating: float = 0
    tags: List[str] = None

class Marketplace:
    """商品商店"""

    def __init__(self, store_path: str = "data/marketplace"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._products = self._load_products()
    
    def _load_products(self) -> Dict[str, Product]:
        products = {}
        
        # 内置商品
        builtin = [
            Product(
                id="code_assistant", name="Code Assistant",
                description="专业的代码编写、调试助手",
                type=ProductType.AGENT, pricing=PricingModel.PAY_PER_USE,
                price=0.01, author="ClawsJoy", version="1.0.0",
                tags=["code", "programming"]
            ),
            Product(
                id="video_producer", name="Video Producer",
                description="AI视频制作技能包",
                type=ProductType.SKILL, pricing=PricingModel.ONE_TIME,
                price=9.99, author="ClawsJoy", version="1.0.0",
                tags=["video", "content"]
            ),
            Product(
                id="security_guard", name="Security Guard",
                description="敏感信息保护管家",
                type=ProductType.TOOL, pricing=PricingModel.SUBSCRIPTION,
                price=4.99, author="ClawsJoy", version="1.0.0",
                tags=["security", "privacy"]
            ),
        ]
        
        for p in builtin:
            products[p.id] = p
        
        return products
    
    def list_products(self, product_type: ProductType = None) -> List[Dict]:
        """列出商品"""
        products = self._products.values()
        if product_type:
            products = [p for p in products if p.type == product_type]
        return [{
            'id': p.id, 'name': p.name, 'description': p.description,
            'type': p.type.value, 'pricing': p.pricing.value, 'price': p.price,
            'rating': p.rating, 'downloads': p.downloads, 'tags': p.tags
        } for p in products]
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)
    
    def purchase(self, user_id: str, product_id: str) -> Dict:
        """用户购买商品"""
        product = self.get_product(product_id)
        if not product:
            return {'success': False, 'error': 'Product not found'}
        
        # 记录购买
        purchase_file = self.store_path / f"{user_id}_purchases.json"
        purchases = []
        if purchase_file.exists():
            with open(purchase_file, 'r') as f:
                purchases = json.load(f)
        
        purchases.append({
            'product_id': product_id,
            'product_name': product.name,
            'price': product.price,
            'purchased_at': datetime.now().isoformat()
        })
        
        with open(purchase_file, 'w') as f:
            json.dump(purchases, f, indent=2)
        
        # 增加下载量
        product.downloads += 1
        
        return {
            'success': True,
            'product': product.name,
            'price': product.price,
            'message': f'成功购买 {product.name}'
        }
    
    def get_user_purchases(self, user_id: str) -> List[Dict]:
        """获取用户已购商品"""
        purchase_file = self.store_path / f"{user_id}_purchases.json"
        if purchase_file.exists():
            with open(purchase_file, 'r') as f:
                return json.load(f)
        return []

marketplace = Marketplace()
