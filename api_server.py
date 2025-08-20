"""
AI Control Tower REST API Server

This FastAPI server provides REST endpoints to test and interact with the AI Control Tower agent
for dynamic baseline creation.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime
import logging
import asyncio
from contextlib import asynccontextmanager

# Import the AI Control Tower agent
from ai_control_tower_agent import run_ai_control_tower, BASELINE_RANGES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response Models
class BaselineRequest(BaseModel):
    """Request model for baseline generation"""
    user_query: str = Field(..., description="User query describing baseline analysis needs", min_length=10)
    document_content: str = Field(..., description="Agent documentation content to analyze", min_length=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_query": "Create baseline metrics for a customer service agent handling technical support",
                "document_content": """
                Customer Service Agent Specification:
                - Handles technical support for cloud services
                - Uses knowledge base, ticketing system, and escalation tools  
                - Expected to resolve 75% of issues on first contact
                - Domain: Mature cloud service support with well-established processes
                - Task complexity: Mix of simple account issues and complex technical problems
                - Performance targets: <15% escalation rate, >70% CSAT
                """
            }
        }

class BaselineResponse(BaseModel):
    """Response model for baseline generation"""
    success: bool
    timestamp: str
    user_query: str
    document_analysis: Dict[str, Any]
    calculated_baselines: Dict[str, Any]
    insights: Dict[str, Any]
    readiness_assessment: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    agent_status: str

class FrameworkRangesResponse(BaseModel):
    """Framework ranges response"""
    baseline_ranges: Dict[str, Any]
    total_categories: int
    total_metrics: int
    description: str

# Global variables for background tasks
analysis_results = {}
analysis_status = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("AI Control Tower API Server starting up...")
    
    # Verify environment variables
    if not os.getenv("OPENROUTER_KEY"):
        logger.warning("OPENROUTER_KEY not found in environment variables")
    
    yield
    
    # Shutdown
    logger.info("AI Control Tower API Server shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="AI Control Tower API",
    description="REST API for Dynamic Baseline Creation using ReAct Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
app.mount("/ui", StaticFiles(directory="UI", html=True), name="ui")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>AI Control Tower API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 3px; font-weight: bold; color: white; }
                .get { background: #27ae60; }
                .post { background: #e74c3c; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Control Tower API</h1>
                <p><strong>Dynamic Baseline Creation using ReAct Agent</strong></p>
                
                <h3>Available Endpoints:</h3>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/health</strong>
                    <p>Health check and system status</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/framework/ranges</strong>
                    <p>Get predefined baseline framework ranges</p>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> <strong>/analyze/baseline</strong>
                    <p>Generate dynamic baselines from agent documentation</p>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> <strong>/analyze/baseline/async</strong>
                    <p>Generate baselines asynchronously (returns task ID)</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/analyze/status/{task_id}</strong>
                    <p>Check status of async baseline analysis</p>
                </div>
                
                <h3>Documentation & Testing:</h3>
                <p>
                    • <a href="/docs" target="_blank">Interactive API Documentation (Swagger UI)</a><br>
                    • <a href="/redoc" target="_blank">Alternative API Documentation (ReDoc)</a><br>
                    • <a href="/ui" target="_blank">Web UI Demo</a>
                </p>
                
                <h3>Quick Test:</h3>
                <p>Try the health check: <a href="/health" target="_blank">/health</a></p>
            </div>
        </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test if OpenRouter key is available
        openrouter_status = "configured" if os.getenv("OPENROUTER_KEY") else "missing"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            agent_status=f"ready (OpenRouter: {openrouter_status})"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/framework/ranges", response_model=FrameworkRangesResponse)
async def get_framework_ranges():
    """Get the predefined baseline framework ranges"""
    try:
        # Count metrics
        total_categories = len(BASELINE_RANGES)
        total_metrics = sum(len(category) for category in BASELINE_RANGES.values())
        
        return FrameworkRangesResponse(
            baseline_ranges=BASELINE_RANGES,
            total_categories=total_categories,
            total_metrics=total_metrics,
            description="Predefined baseline ranges used by the AI Control Tower framework for dynamic baseline generation"
        )
    except Exception as e:
        logger.error(f"Failed to get framework ranges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get framework ranges: {str(e)}")

@app.post("/analyze/baseline", response_model=BaselineResponse)
async def analyze_baseline(request: BaselineRequest):
    """Generate dynamic baselines from agent documentation (synchronous)"""
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting baseline analysis for query: {request.user_query[:50]}...")
        
        # Run the AI Control Tower agent
        result = run_ai_control_tower(request.user_query, request.document_content)
        
        # Extract results
        final_report = result.get('final_report', {})
        analysis = final_report.get('analysis', {})
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = BaselineResponse(
            success=True,
            timestamp=datetime.now().isoformat(),
            user_query=request.user_query,
            document_analysis=analysis.get('document_analysis', {}),
            calculated_baselines=analysis.get('baseline_calculations', {}).get('calculated_baselines', {}),
            insights=analysis.get('comparison_results', {}).get('insights', {}),
            readiness_assessment=analysis.get('comparison_results', {}).get('readiness_assessment', {}),
            execution_time=execution_time
        )
        
        logger.info(f"Baseline analysis completed in {execution_time:.2f} seconds")
        return response
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Baseline analysis failed: {str(e)}")
        
        return BaselineResponse(
            success=False,
            timestamp=datetime.now().isoformat(),
            user_query=request.user_query,
            document_analysis={},
            calculated_baselines={},
            insights={},
            readiness_assessment={},
            error=str(e),
            execution_time=execution_time
        )

async def run_baseline_analysis_async(task_id: str, request: BaselineRequest):
    """Run baseline analysis asynchronously"""
    try:
        analysis_status[task_id] = {"status": "running", "started_at": datetime.now().isoformat()}
        
        # Run the AI Control Tower agent
        result = run_ai_control_tower(request.user_query, request.document_content)
        
        # Store results
        analysis_results[task_id] = {
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "result": result
        }
        analysis_status[task_id]["status"] = "completed"
        
    except Exception as e:
        logger.error(f"Async baseline analysis failed for task {task_id}: {str(e)}")
        analysis_results[task_id] = {
            "status": "failed",
            "completed_at": datetime.now().isoformat(),
            "error": str(e)
        }
        analysis_status[task_id]["status"] = "failed"

@app.post("/analyze/baseline/async")
async def analyze_baseline_async(request: BaselineRequest, background_tasks: BackgroundTasks):
    """Generate dynamic baselines asynchronously (returns task ID)"""
    try:
        # Generate unique task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.user_query) % 10000}"
        
        # Start background task
        background_tasks.add_task(run_baseline_analysis_async, task_id, request)
        
        logger.info(f"Started async baseline analysis with task ID: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Baseline analysis started. Use /analyze/status/{task_id} to check progress.",
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start async baseline analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/analyze/status/{task_id}")
async def get_analysis_status(task_id: str):
    """Check status of async baseline analysis"""
    try:
        if task_id not in analysis_status:
            raise HTTPException(status_code=404, detail="Task ID not found")
        
        status_info = analysis_status[task_id]
        
        if status_info["status"] == "completed" and task_id in analysis_results:
            result_data = analysis_results[task_id]
            final_report = result_data["result"].get('final_report', {})
            analysis = final_report.get('analysis', {})
            
            return {
                "task_id": task_id,
                "status": "completed",
                "completed_at": result_data["completed_at"],
                "result": {
                    "success": True,
                    "document_analysis": analysis.get('document_analysis', {}),
                    "calculated_baselines": analysis.get('baseline_calculations', {}).get('calculated_baselines', {}),
                    "insights": analysis.get('comparison_results', {}).get('insights', {}),
                    "readiness_assessment": analysis.get('comparison_results', {}).get('readiness_assessment', {})
                }
            }
        elif status_info["status"] == "failed" and task_id in analysis_results:
            result_data = analysis_results[task_id]
            return {
                "task_id": task_id,
                "status": "failed",
                "completed_at": result_data["completed_at"],
                "error": result_data["error"]
            }
        else:
            return {
                "task_id": task_id,
                "status": status_info["status"],
                "started_at": status_info["started_at"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/analyze/results")
async def list_analysis_results():
    """List all analysis results (for debugging)"""
    return {
        "active_tasks": len(analysis_status),
        "completed_results": len(analysis_results),
        "tasks": {
            task_id: {"status": status["status"], "started_at": status["started_at"]}
            for task_id, status in analysis_status.items()
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "available_endpoints": ["/health", "/framework/ranges", "/analyze/baseline"]}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {"error": "Internal server error", "message": "Please check server logs for details"}

if __name__ == "__main__":
    import uvicorn
    
    # Check for environment variables
    if not os.getenv("OPENROUTER_KEY"):
        print("⚠️  WARNING: OPENROUTER_KEY not found in environment variables")
        print("   The AI Control Tower agent may not work without this key.")
        print("   Please set OPENROUTER_KEY in your .env file.")
    
    print("\n🚀 Starting AI Control Tower API Server...")
    print("📋 Available at:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Alternative Docs: http://localhost:8000/redoc") 
    print("   • Web UI Demo: http://localhost:8000/ui")
    print("   • Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "api_server:app",  # Use string import for reload compatibility
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )