from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.mongodb_agent import MongoDBAgent

app = FastAPI(title="NoSQL Agent API", version="1.0.0")
mongodb_agent = MongoDBAgent()

class QueryRequest(BaseModel):
    natural_query: str

class QueryResponse(BaseModel):
    result: str

@app.post("/query", response_model=QueryResponse)
async def run_query(query: QueryRequest):
    try:
        result = mongodb_agent.run_query(query.natural_query)
        return QueryResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))