from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from config import PORT
from master_agent import orchestrate_generation
import json

app = FastAPI(
    title="MultiAgent AI Website Generator",
    description="Generate full-stack web applications using AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {
        "message": "MultiAgent AI Website Generator Backend 🚀",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "preview": "/preview/{project_name} (GET)",
            "download": "/download/{project_name} (GET)"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "agents": {
            "prompt_enhancer": "DeepSeek",
            "frontend_generator": "Gemini",
            "backend_generator": "Gemini"
        }
    }

@app.post("/generate")
async def generate_website(request: PromptRequest):
    """
    Main endpoint: Generate complete full-stack application
    """
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 10 characters long"
        )
    
    print(f"📝 Received prompt: {request.prompt}")
    
    result = await orchestrate_generation(request.prompt)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {result.get('error')} - {result.get('details')}"
        )
    
    return {
        "status": "success",
        "message": "Website generated successfully!",
        "data": result
    }

@app.get("/preview/{project_name}")
async def preview_project(project_name: str):
    """
    Get generated project structure for preview
    """
    project_path = Path("generated") / project_name
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Read frontend files for preview
        frontend_files = []
        frontend_path = project_path / "frontend"
        
        if frontend_path.exists():
            for file_path in frontend_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.tsx', '.ts', '.jsx', '.js', '.css']:
                    rel_path = file_path.relative_to(frontend_path)
                    content = file_path.read_text(encoding='utf-8')
                    frontend_files.append({
                        "path": str(rel_path),
                        "content": content,
                        "type": file_path.suffix[1:]
                    })
        
        return {
            "status": "success",
            "project_name": project_name,
            "frontend_files": frontend_files[:10],  # Limit to 10 files for preview
            "total_files": len(frontend_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{project_name}")
async def download_project(project_name: str):
    """
    Download complete project as ZIP
    """
    zip_path = Path("generated") / f"{project_name}.zip"
    
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"{project_name}.zip"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
