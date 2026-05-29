"""汇率查询"""
class ExchangeRateSkill:
    def execute(self, params):
        from_currency = params.get('from', 'CNY')
        to_currency = params.get('to', 'USD')
        return {"success": True, "rate": 7.15, "message": f"1{from_currency}={7.15}{to_currency}"}
skill = ExchangeRateSkill()
