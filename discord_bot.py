#!/usr/bin/env python3
"""ClawsJoy Discord Bot — 全自动回复，独立记忆"""
import os
import discord
import requests
import aiohttp
from dotenv import load_dotenv

load_dotenv("config/.env")

# ========== 配置 ==========
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
CLAWSJOY_URL = "http://localhost:5002/v5/execute"
PROXY_URL = "http://127.0.0.1:7890"

if not DISCORD_TOKEN:
    print("❌ 请在 config/.env 中设置 DISCORD_BOT_TOKEN")
    exit(1)

# ========== 自定义 HTTP 会话（走代理）==========
class ProxiedHTTPClient(discord.http.HTTPClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 替换 __session 为带代理的会话
        connector = aiohttp.TCPConnector()
        self.__session = aiohttp.ClientSession(connector=connector)

    async def request(self, route, **kwargs):
        kwargs["proxy"] = PROXY_URL
        return await super().request(route, **kwargs)

# ========== Discord 客户端 ==========
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, http_client=ProxiedHTTPClient)

@client.event
async def on_ready():
    print(f"✅ {client.user} 已上线")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.bot:
        return

    user_input = message.content.strip()
    if not user_input:
        return

    print(f"📥 {message.author.name}: {user_input}")

    try:
        response = requests.post(
            CLAWSJOY_URL,
            json={
                "raw_input": user_input,
                "user_id": f"discord_{message.author.id}",
            },
            timeout=60
        )
        result = response.json()
        reply = result.get("response") or result.get("output_content", "嗯？")
    except Exception as e:
        reply = f"出错了：{e}"

    print(f"📤 → {message.author.name}: {reply[:80]}...")
    if len(reply) <= 2000:
        await message.channel.send(reply)
    else:
        for i in range(0, len(reply), 2000):
            await message.channel.send(reply[i:i+2000])

if __name__ == "__main__":
    print("🚀 ClawsJoy Discord Bot 启动...")
    client.run(DISCORD_TOKEN)
