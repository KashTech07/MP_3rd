
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agent.graph import workflow


# FastAPI application creation
app = FastAPI(
    title="Groundwater AI Analyst",
    description="API for groundwater data analysis",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request model
class QueryRequest(BaseModel):
    query: str


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Groundwater AI Analyst API is running"
    }


# Analyze endpoint
@app.post("/analyze")
def analyze(request: QueryRequest):

    query = request.query.strip()

    # Check for empty input
    if not query:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid question."
        )

    # Execute LangGraph workflow
    try:
        result = workflow.invoke({
            "query": query
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )

    # Return the generated response
    return {
        "response": result.get("response", "No response generated.")
    }
