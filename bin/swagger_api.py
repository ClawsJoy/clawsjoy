#!/usr/bin/env python3
"""ClawsJoy API 文档服务 - Swagger UI"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields

app = Flask(__name__)
CORS(app)

# 配置 Swagger
api = Api(
    app,
    version='2.0.0',
    title='ClawsJoy API 文档',
    description='ClawsJoy 多租户 AI 调度平台 API 文档',
    doc='/docs',
    prefix='/api'
)

# ============ 命名空间 ============
auth_ns = api.namespace('auth', description='认证服务')
tenant_ns = api.namespace('tenant', description='租户管理')
billing_ns = api.namespace('billing', description='计费系统')
coffee_ns = api.namespace('coffee', description='咖啡订购')
workflow_ns = api.namespace('workflow', description='Workflow 引擎')

# ============ 模型定义 ============
login_model = api.model('Login', {
    'username': fields.String(required=True, description='用户名', example='admin'),
    'password': fields.String(required=True, description='密码', example='admin123')
})

tenant_model = api.model('Tenant', {
    'id': fields.String(description='租户ID', example='1'),
    'name': fields.String(description='租户名称', example='租户 1')
})

balance_model = api.model('Balance', {
    'tenant_id': fields.String(description='租户ID', example='1'),
    'balance': fields.Float(description='余额', example=100.0)
})

order_model = api.model('Order', {
    'item': fields.String(description='咖啡类型', example='拿铁'),
    'shop_id': fields.Integer(description='店铺ID', example=1)
})

# ============ 认证 API ============
@auth_ns.route('/login')
class AuthLogin(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, '成功', login_model)
    def post(self):
        """用户登录"""
        return {"success": True, "token": "eyJhbGci...", "user": {"name": "admin", "tenant_id": "0", "role": "admin"}}

@auth_ns.route('/health')
class AuthHealth(Resource):
    def get(self):
        """健康检查"""
        return {"status": "ok", "service": "auth"}

# ============ 租户 API ============
@tenant_ns.route('/')
class TenantList(Resource):
    @tenant_ns.marshal_list_with(tenant_model)
    def get(self):
        """获取所有租户"""
        return [{"id": "1", "name": "租户 1"}, {"id": "2", "name": "租户 2"}]

@tenant_ns.route('/<string:tenant_id>')
class TenantDetail(Resource):
    def get(self, tenant_id):
        """获取指定租户"""
        return {"id": tenant_id, "name": f"租户 {tenant_id}", "config": {"evolution_enabled": True}}

# ============ 计费 API ============
@billing_ns.route('/balance')
class BillingBalance(Resource):
    @billing_ns.param('tenant_id', '租户ID')
    @billing_ns.marshal_with(balance_model)
    def get(self):
        """查询余额"""
        return {"tenant_id": "1", "balance": 100.0}

@billing_ns.route('/recharge')
class BillingRecharge(Resource):
    @billing_ns.expect(api.model('Recharge', {'amount': fields.Float(required=True)}))
    def post(self):
        """充值"""
        return {"success": True, "new_balance": 200.0}

# ============ 咖啡 API ============
@coffee_ns.route('/shops')
class CoffeeShops(Resource):
    def get(self):
        """获取咖啡店列表"""
        return {
            "success": True,
            "shops": [
                {"id": 1, "name": "星巴克", "distance": "200m", "rating": 4.8},
                {"id": 2, "name": "瑞幸", "distance": "350m", "rating": 4.6}
            ]
        }

@coffee_ns.route('/order')
class CoffeeOrder(Resource):
    @coffee_ns.expect(order_model)
    def post(self):
        """下单"""
        return {"success": True, "order_id": "ORD_001", "message": "下单成功"}

# ============ Workflow API ============
@workflow_ns.route('/list')
class WorkflowList(Resource):
    def get(self):
        """获取 Workflow 列表"""
        return {"workflows": []}

@workflow_ns.route('/detail')
class WorkflowDetail(Resource):
    @workflow_ns.param('workflow_id', 'Workflow ID')
    def get(self):
        """获取 Workflow 详情"""
        return {"workflow_id": "test_001", "status": "completed", "steps": []}

# ============ 首页 ============
@app.route('/')
def index():
    return jsonify({
        "service": "ClawsJoy API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "auth": "/api/auth/login",
            "tenant": "/api/tenants",
            "billing": "/api/billing/balance",
            "coffee": "/api/coffee/shops",
            "workflow": "/api/workflow/list"
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("📚 ClawsJoy API 文档服务")
    print("=" * 50)
    print("🌐 Swagger UI: http://redis:8094/api/docs")
    print("📡 API 根路径: http://redis:8094/")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8094, debug=False)
