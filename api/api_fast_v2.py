"""FastAPI 版本 - 新版 ChromaDB"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

app = FastAPI(title="ClawsJoy AI", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    success: bool
    response: str
    user_id: str
    intent: Optional[str] = None


from core.llm_enhanced import llm_enhanced
from core.chroma_v2 import ChromaStoreV2
from core.prompt_engineer import prompt_engineer


@app.get("/health")
async def health():
    return {"status": "ok", "service": "clawsjoy-ai", "version": "5.0.0"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="message required")
    
    store = ChromaStoreV2(request.user_id)
    similar = store.search(request.message, limit=2)
    
    context = ""
    if similar:
        context = "\n相关记忆:\n" + "\n".join([f"- {s['text'][:100]}" for s in similar])
    
    prompt = f"{context}\n用户: {request.message}\n助手:"
    response = llm_enhanced.generate(prompt)
    
    store.add(f"用户: {request.message}\n助手: {response[:200]}")
    
    return ChatResponse(
        success=True,
        response=response,
        user_id=request.user_id,
        intent="chat"
    )


@app.post("/api/chain-of-thought")
async def chain_of_thought(request: ChatRequest):
    prompt = prompt_engineer.reasoning_prompt(request.message)
    response = llm_enhanced.generate(prompt, temperature=0.3)
    return {"success": True, "response": response}


if __name__ == "__main__":
    print("🚀 FastAPI 启动 (新版 ChromaDB): http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
