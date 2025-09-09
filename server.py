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
async def proxy_claude_api(request: ChatRequest):
    """Claude API 프록시 엔드포인트"""
    
    # API 키 확인
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Claude API key not configured. Please set CLAUDE_API_KEY environment variable."
        )
    
    # Claude API 호출
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": "You are RAPTOR, an AI assistant specialized in root cause analysis and causal relationship identification. You help users understand complex systems through ontology-based reasoning to identify root causes of problems.",
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Claude API error: {response.text}"
                )
            
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request to Claude API timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Claude API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)