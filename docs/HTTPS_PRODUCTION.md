# 生产环境 HTTPS 证书配置

## 1. 使用 Let's Encrypt (免费)

```bash
# 安装 certbot
sudo apt install certbot

# 获取证书（需要域名）
sudo certbot certonly --standalone -d yourdomain.com

# 证书位置
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
2. 使用自签名证书（开发/测试）
# 已生成
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -days 365 \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=ClawsJoy/CN=localhost"
3. 使用商业证书
生成 CSR

提交给 CA 机构

安装证书到 ssl/ 目录

4. 配置更新
修改各服务启动脚本，使用生产证书路径：
ssl_context=('/path/to/fullchain.pem', '/path/to/privkey.pem')
