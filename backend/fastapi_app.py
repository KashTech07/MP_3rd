from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graph import workflow

app = FastAPI(
    title="Groundwater AI Analyst API",
    description="Backend API powered by LangGraph and Gemini for groundwater data analysis.",
    version="1.0.0"
)

# Enable CORS so your teammates' frontend can connect without issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (restrict this to specific frontend URLs in production if needed)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body schema
class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Groundwater AI Analyst Backend is running!"}

@app.post("/analyze")
def analyze_groundwater(request: QueryRequest):
    try:
        # Invoke the LangGraph workflow with the incoming query
        result = workflow.invoke({"query": request.query})
        
        return {
            "query": request.query,
            "response": result.get("response", "No response generated.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))