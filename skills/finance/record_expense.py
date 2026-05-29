"""记录支出"""
class RecordExpenseSkill:
    def execute(self, params):
        amount = params.get('amount', 0)
        category = params.get('category', '')
        date = params.get('date', '')
        return {"success": True, "expense_id": f"EXP_{hash(str(amount))}", "message": f"已记录支出 ¥{amount}"}
skill = RecordExpenseSkill()
