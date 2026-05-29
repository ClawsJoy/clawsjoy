"""添加客户"""
class AddCustomerSkill:
    def execute(self, params):
        name = params.get('name', '')
        phone = params.get('phone', '')
        company = params.get('company', '')
        return {"success": True, "customer_id": f"CUS_{hash(name)}", "message": f"已添加客户: {name}"}
skill = AddCustomerSkill()
