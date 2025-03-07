from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
import datetime
import uuid
import json
import traceback
from contextlib import asynccontextmanager

# Import the CodeReviewAssistant class
from .main import CodeReviewAssistant

# Models
class FileContext(BaseModel):
    before: List[str] = Field(default_factory=list)
    after: List[str] = Field(default_factory=list)

class FileInfo(BaseModel):
    fileName: str
    status: str
    codeContext: Optional[FileContext] = None

class DiffData(BaseModel):
    summary: Dict[str, Any]
    files: List[FileInfo]

class CodeData(BaseModel):
    code: str
    filename: Optional[str] = None
    file_extension: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def hello_world():\n    print('Hello, world!')",
                "filename": "hello.py",
                "file_extension": ".py"
            }
        }

class AnalysisRequest(BaseModel):
    project_id: Optional[str] = None
    dff_data: Optional[DiffData] = None
    code_data: Optional[CodeData] = None
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "my-project-123",
                "code_data": {
                    "code": "def hello_world():\n    print('Hello, world!')",
                    "filename": "hello.py"
                }
            }
        }
    
    @validator('dff_data', 'code_data')
    def validate_data_provided(cls, v, values):
        # Ensure at least one of dff_data or code_data is provided
        if 'dff_data' not in values and 'code_data' not in values and not v:
            raise ValueError('Either dff_data or code_data must be provided')
        return v

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    project_id: Optional[str] = None

# In-memory store for results
analysis_results = {}

# Context manager to initialize the assistant
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the assistant when the app starts
    app.state.assistant = CodeReviewAssistant()
    await app.state.assistant.initialize()
    print("✅ CodeReviewAssistant initialized")
    yield
    # Clean up when the app shuts down
    print("Shutting down CodeReviewAssistant...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Code Review Assistant API",
    description="""
    API for automatic code analysis using advanced AI techniques.
    
    ## Features
    
    * Source code analysis in multiple languages
    * Security issue detection
    * Performance evaluation
    * Best practices verification
    * Synchronous and asynchronous analysis
    
    ## Workflow
    
    1. Submit your code for analysis using the `/analyze` (synchronous) or `/analyze/async` (asynchronous) endpoint
    2. For asynchronous analysis, check the result using the `/analysis/{analysis_id}` endpoint
    3. Explore previous analyses with the `/analyses` endpoint
    """,
    version="0.1.0",
    contact={
        "name": "Development Team",
        "url": "https://github.com/your-username/code-review-assistant",
        "email": "your-email@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "details": exc.errors(),
            "data": exc.body
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    print(f"Unhandled exception: {str(exc)}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc)
        }
    )

# Helper function to get the assistant
async def get_assistant():
    return app.state.assistant

@app.get("/health")
async def health_check():
    """
    Check the API status.
    
    Returns:
        dict: An object with the current status and timestamp.
    """
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: AnalysisRequest):
    """Analyze code synchronously."""
    try:
        analysis_id = str(uuid.uuid4())
        created_at = datetime.datetime.now().isoformat()
        
        # Almacena estado inicial
        analysis_results[analysis_id] = {
            "status": "processing",
            "created_at": created_at,
            "project_id": request.project_id
        }
        
        # Obtiene el asistente del estado de la app
        assistant = app.state.assistant
        
        # Procesa la solicitud
        if request.dff_data:
            result = await assistant.analyze_diff(request.dff_data.dict())
        elif request.code_data:
            result = await assistant.review_code(request.code_data.dict())
        else:
            raise HTTPException(
                status_code=400,
                detail="No code or DFF data provided"
            )
        
        # Actualiza el resultado
        completed_at = datetime.datetime.now().isoformat()
        analysis_results[analysis_id] = {
            "status": "completed",
            "result": result,
            "created_at": created_at,
            "completed_at": completed_at,
            "project_id": request.project_id
        }
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "result": result,
            "created_at": created_at,
            "completed_at": completed_at,
            "project_id": request.project_id
        }
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/async", response_model=AnalysisResponse)
async def analyze_code_async(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start asynchronous code analysis."""
    analysis_id = str(uuid.uuid4())
    created_at = datetime.datetime.now().isoformat()
    
    # Almacena estado inicial
    analysis_results[analysis_id] = {
        "status": "pending",
        "created_at": created_at,
        "project_id": request.project_id
    }
    
    # Define la tarea en segundo plano
    async def perform_analysis():
        try:
            # Actualizar estado a "processing"
            analysis_results[analysis_id]["status"] = "processing"
            
            assistant = app.state.assistant
            if request.dff_data:
                result = await assistant.analyze_diff(request.dff_data.dict())
            elif request.code_data:
                result = await assistant.review_code(request.code_data.dict())
            else:
                raise ValueError("No code or DFF data provided")
            
            # Actualiza el resultado
            completed_at = datetime.datetime.now().isoformat()
            analysis_results[analysis_id].update({
                "status": "completed",
                "result": result,
                "completed_at": completed_at
            })
        except Exception as e:
            print(f"Error in async analysis: {str(e)}")
            print(traceback.format_exc())
            analysis_results[analysis_id].update({
                "status": "error",
                "error": str(e)
            })
    
    # Agrega la tarea al background
    background_tasks.add_task(perform_analysis)
    
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Analysis started in background",
        "created_at": created_at,
        "project_id": request.project_id
    }

@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(analysis_id: str):
    """Get the results of a specific analysis."""
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    analysis = analysis_results[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": analysis.get("status", "unknown"),
        "message": analysis.get("error") if analysis.get("status") == "error" else None,
        "result": analysis.get("result"),
        "created_at": analysis.get("created_at"),
        "completed_at": analysis.get("completed_at"),
        "project_id": analysis.get("project_id")
    }

@app.get("/analyses")
async def list_analyses(
    project_id: Optional[str] = None, 
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List performed analyses with pagination.
    """
    filtered_analyses = [
        {
            "analysis_id": analysis_id,
            "status": data.get("status", "unknown"),
            "created_at": data.get("created_at"),
            "project_id": data.get("project_id"),
            "completed_at": data.get("completed_at")
        }
        for analysis_id, data in analysis_results.items()
        if project_id is None or data.get("project_id") == project_id
    ]
    
    filtered_analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    paginated = filtered_analyses[offset:offset + limit]
    
    return {
        "total": len(filtered_analyses),
        "offset": offset,
        "limit": limit,
        "analyses": paginated
    }

@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete a specific analysis.
    
    Args:
        analysis_id: The unique ID of the analysis to delete.
    
    Returns:
        dict: Confirmation message.
        
    Raises:
        HTTPException: If the analysis is not found.
    """
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Delete the analysis
    del analysis_results[analysis_id]
    
    return {"status": "success", "message": f"Analysis {analysis_id} deleted"}

@app.get("/stats")
async def get_stats():
    """
    Get statistics about performed analyses.
    
    Returns:
        dict: Statistics including total analyses, completed, pending,
              with error, and success rate.
    """
    total_analyses = len(analysis_results)
    completed = sum(1 for data in analysis_results.values() if data.get("status") == "completed")
    pending = sum(1 for data in analysis_results.values() if data.get("status") == "pending")
    error = sum(1 for data in analysis_results.values() if data.get("status") == "error")
    
    return {
        "total_analyses": total_analyses,
        "completed": completed,
        "pending": pending,
        "error": error,
        "success_rate": (completed / total_analyses * 100) if total_analyses > 0 else 0
    } 