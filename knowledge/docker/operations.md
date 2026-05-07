# Docker 运维

## 常见问题
1. 容器未运行: docker start <name>
2. 端口冲突: docker stop <name> && docker rm <name>
3. 日志过大: docker logs <name> --tail 100

## Compose 管理
docker-compose up -d web redis tts
docker-compose down
docker-compose logs -f

## 故障排查
docker ps -a                    # 查看所有容器
docker inspect <name>           # 查看详细信息
docker logs <name> --tail 50    # 查看日志
