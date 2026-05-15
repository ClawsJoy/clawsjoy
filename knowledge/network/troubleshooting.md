# 网络故障排查

## 端口检查
ss -tlnp | grep <port>          # 查看端口监听
sudo lsof -i :<port>            # 查看占用进程
netstat -an | grep <port>       # 网络连接

## 服务连通性
curl -v http://localhost:18109/api/agent
telnet localhost 18109

## 常见问题
1. Connection refused → 服务未启动
2. Address already in use → 端口冲突
3. Timeout → 防火墙或代理问题
