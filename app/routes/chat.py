from fastapi import APIRouter
from pydantic import BaseModel
from app.services.search.functions import retrieve_context
from app.services.llm.functions import llm_call
import asyncio

router = APIRouter(prefix="/chat")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    context_chunks = await asyncio.to_thread(retrieve_context, request.query)
    answer = await asyncio.to_thread(llm_call, context_chunks, request.query)
    
    return ChatResponse(answer=answer)
