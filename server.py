from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from typing import List

# 환경변수 로드
load_dotenv()

app = FastAPI(title="RAPTOR API Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델들
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    content: List[dict]
    id: str
    model: str
    role: str
    stop_reason: str
    usage: dict

@app.get("/")
async def root():
    return {"message": "🦖 RAPTOR API Server is running!"}

@app.post("/api/claude/messages", response_model=dict)
async def proxy_ollama_api(request: ChatRequest):
    """Ollama API 프록시 엔드포인트"""
    
    # Ollama 서버 URL (기본값: localhost:11434)
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
    
    # Ollama API 호출을 위한 메시지 형식 변환
    messages = []
    system_message = "You are RAPTOR, an AI assistant specialized in root cause analysis and causal relationship identification. You help users understand complex systems through ontology-based reasoning to identify root causes of problems."
    
    # 시스템 메시지를 첫 번째 메시지로 추가
    messages.append({"role": "system", "content": system_message})
    
    # 사용자 메시지들 추가
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ollama_url}/api/chat",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama API error: {response.text}"
                )
            
            ollama_response = response.json()
            
            # Claude API 형식으로 응답 변환
            claude_format_response = {
                "content": [{"text": ollama_response["message"]["content"]}],
                "id": "ollama-" + str(hash(ollama_response["message"]["content"]))[:10],
                "model": model,
                "role": "assistant",
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            }
            
            return claude_format_response
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request to Ollama API timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Ollama API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)