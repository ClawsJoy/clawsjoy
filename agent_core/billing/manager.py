import json
from pathlib import Path
from datetime import datetime

class BillingManager:
    def __init__(self):
        self.billing_dir = Path("data/billing")
        self.billing_dir.mkdir(parents=True, exist_ok=True)
    
    def deduct(self, tenant_id: str, user_id: str, amount: float, reason: str) -> dict:
        user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
        if not user_file.exists():
            return {'success': False, 'error': 'User not found'}
        
        with open(user_file, 'r') as f:
            user = json.load(f)
        
        current = user.get('balance', 0)
        if current < amount:
            return {'success': False, 'error': 'Insufficient balance'}
        
        new_balance = current - amount
        user['balance'] = new_balance
        
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
        
        self._record_transaction(tenant_id, user_id, -amount, reason, new_balance)
        return {'success': True, 'balance': new_balance}
    
    def add_balance(self, tenant_id: str, user_id: str, amount: float, reason: str = "recharge") -> dict:
        user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
        if not user_file.exists():
            return {'success': False, 'error': 'User not found'}
        
        with open(user_file, 'r') as f:
            user = json.load(f)
        
        new_balance = user.get('balance', 0) + amount
        user['balance'] = new_balance
        
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
        
        self._record_transaction(tenant_id, user_id, amount, reason, new_balance)
        return {'success': True, 'balance': new_balance}
    
    def get_balance(self, tenant_id: str, user_id: str) -> float:
        user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
        if not user_file.exists():
            return 0
        with open(user_file, 'r') as f:
            user = json.load(f)
        return user.get('balance', 0)
    
    def _record_transaction(self, tenant_id, user_id, amount, reason, balance):
        trans_file = self.billing_dir / f"{tenant_id}_{user_id}.json"
        transactions = []
        if trans_file.exists():
            with open(trans_file, 'r') as f:
                transactions = json.load(f)
        transactions.append({
            'amount': amount, 'reason': reason, 'balance': balance,
            'timestamp': datetime.now().isoformat()
        })
        with open(trans_file, 'w') as f:
            json.dump(transactions[-100:], f, indent=2)
    
    def get_transactions(self, tenant_id: str, user_id: str) -> list:
        trans_file = self.billing_dir / f"{tenant_id}_{user_id}.json"
        if trans_file.exists():
            with open(trans_file, 'r') as f:
                return json.load(f)
        return []

billing = BillingManager()
