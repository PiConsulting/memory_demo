"""
Mini API Demo with Agent and Memory Integration
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from memory_demo.azure.agents.customer_agent import CustomerAgent

load_dotenv()

app = FastAPI(
    title="Customer Agent API",
    description="Demo API with Azure AI Agent and Memory Store",
    version="1.0.0"
)

# Global agent instance
agent = None


def get_agent() -> CustomerAgent:
    """Get or initialize the customer agent"""
    global agent
    if agent is None:
        agent = CustomerAgent()
    return agent


# ============ Pydantic Models ============

class ChatRequest(BaseModel):
    message: str
    customer_id: str = "customer001"


class ChatResponse(BaseModel):
    message: str
    customer_id: str
    status: str = "success"


class MemoryRequest(BaseModel):
    content: str
    customer_id: str = "customer001"


class MemorySearchRequest(BaseModel):
    query: str | None = None
    customer_id: str = "customer001"


class MemoryResponse(BaseModel):
    memories: list
    customer_id: str
    count: int
    status: str = "success"


# ============ Routes ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Customer Agent API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the customer agent.
    
    Args:
        request: ChatRequest with message and customer_id
        
    Returns:
        ChatResponse with agent response
    """
    try:
        agent = get_agent()
        response = agent.chat(
            user_message=request.message,
            customer_id=request.customer_id
        )
        return ChatResponse(
            message=response,
            customer_id=request.customer_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/add", response_model=MemoryResponse)
async def add_memory(request: MemoryRequest):
    """
    Add a memory entry for a customer.
    
    Args:
        request: MemoryRequest with content and customer_id
        
    Returns:
        MemoryResponse confirming storage
    """
    try:
        agent = get_agent()
        agent.add_memory(
            content=request.content,
            customer_id=request.customer_id
        )
        return MemoryResponse(
            memories=[request.content],
            customer_id=request.customer_id,
            count=1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/search", response_model=MemoryResponse)
async def search_memories(request: MemorySearchRequest):
    """
    Search customer memories.
    
    Args:
        request: MemorySearchRequest with optional query and customer_id
        
    Returns:
        MemoryResponse with matching memories
    """
    try:
        agent = get_agent()
        memories = agent.search_memories(
            query=request.query,
            customer_id=request.customer_id
        )
        return MemoryResponse(
            memories=memories,
            customer_id=request.customer_id,
            count=len(memories)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/list/{customer_id}", response_model=MemoryResponse)
async def list_memories(customer_id: str = "customer001"):
    """
    List all memories for a customer.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        MemoryResponse with all customer memories
    """
    try:
        agent = get_agent()
        memories = agent.search_memories(customer_id=customer_id)
        return MemoryResponse(
            memories=memories,
            customer_id=customer_id,
            count=len(memories)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Info Endpoint ============

@app.get("/info")
async def info():
    """Get API information"""
    return {
        "title": "Customer Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "add_memory": "POST /memory/add",
            "search_memory": "POST /memory/search",
            "list_memories": "GET /memory/list/{customer_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
