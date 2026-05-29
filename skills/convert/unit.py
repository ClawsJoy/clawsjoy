"""单位换算"""
class UnitConvertSkill:
    def execute(self, params):
        value = params.get('value', 0)
        from_unit = params.get('from', '')
        to_unit = params.get('to', '')
        
        conversions = {
            ('km', 'm'): lambda x: x * 1000,
            ('m', 'km'): lambda x: x / 1000,
            ('kg', 'g'): lambda x: x * 1000,
            ('g', 'kg'): lambda x: x / 1000,
        }
        
        convert_func = conversions.get((from_unit, to_unit))
        if convert_func:
            result = convert_func(value)
            return {"success": True, "result": result}
        return {"success": False, "error": "不支持的单位换算"}
skill = UnitConvertSkill()
