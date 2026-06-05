#!/usr/bin/env python3
#!/usr/bin/env python3
"""Api Final Fixed - Api Final Fixed 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.chroma_fixed import ChromaFixed
from core.llm_client import LLMClient

app = FastAPI(title="ClawsJoy AI", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    success: bool
    response: str
    user_id: str
    memory_used: Optional[List[str]] = None


llm = LLMClient()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "clawsjoy-ai", "version": "5.0.0"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        store = ChromaFixed(request.user_id)

        # 搜索相关记忆
        memories = store.search(request.message, n_results=3)
        memory_texts = [m["text"] for m in memories if m.get("similarity", 0) > 0.3]

        # 构建 prompt
        prompt = request.message
        if memory_texts:
            prompt = (
                f"相关记忆：\n"
                + "\n".join(memory_texts)
                + f"\n\n用户问题：{request.message}"
            )

        # 调用 LLM
        response = llm.chat(prompt)

        # 保存偏好（metadata 必须有内容）
        if "喜欢" in request.message or "偏好" in request.message:
            store.add(
                text=f"用户偏好: {request.message}",
                metadata={
                    "type": "preference",
                    "timestamp": str(__import__("time").time()),
                },
            )

        return ChatResponse(
            success=True,
            response=response,
            user_id=request.user_id,
            memory_used=memory_texts if memory_texts else None,
        )

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()
        return ChatResponse(
            success=False, response=f"处理失败: {str(e)}", user_id=request.user_id
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
