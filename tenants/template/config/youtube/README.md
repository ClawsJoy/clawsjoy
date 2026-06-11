# YouTube 凭证配置（每个租户独立）

## 配置步骤

1. 访问 https://console.cloud.google.com/
2. 创建项目 → 启用 YouTube Data API v3
3. 创建 OAuth 2.0 客户端 ID（桌面应用）
4. 下载 JSON，放到本目录
5. 重命名为 `client_secrets.json`
6. 运行授权：python3 agents/youtube_uploader.py --tenant 租户ID
