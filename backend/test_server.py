from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path
from typing import Dict

app = FastAPI(title="SkyGram Test Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test endpoints
@app.get("/")
async def root():
    return {
        "message": "Test server is operational",
        "endpoints": {
            "health_check": "/health",
            "test_upload": "/test-upload (POST)",
            "mock_processing": "/mock-process (POST)"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "gemini": "mock",
            "huggingface": "mock"
        }
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload handling"""
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files accepted")
        
        # Create test directory if not exists
        test_dir = Path("test_uploads")
        test_dir.mkdir(exist_ok=True)
        
        # Save test file
        file_id = str(uuid.uuid4())
        file_path = test_dir / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return JSONResponse({
            "status": "success",
            "file_id": file_id,
            "original_name": file.filename,
            "saved_path": str(file_path),
            "size_kb": len(content) / 1024
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test upload failed: {str(e)}")

@app.post("/mock-process")
async def mock_process(file: UploadFile = File(...)):
    """Full mock of the processing pipeline"""
    mock_objects = ["dragon", "dog", "castle", "face", "ship"]
    mock_captions = [
        "Test mode: Cloud imagination activated!",
        "This would be your generated artwork",
        "Mock cloud transformation complete"
    ]
    
    try:
        # Simulate processing delay
        import time
        time.sleep(1.5)  # Simulate AI processing time
        
        return JSONResponse({
            "session_id": str(uuid.uuid4()),
            "detected_object": mock_objects[int(time.time()) % len(mock_objects)],
            "caption": mock_captions[int(time.time()) % len(mock_captions)],
            "original_url": "/mock/original.jpg",
            "generated_url": "/mock/artwork.jpg",
            "status": "success"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n🛠️  Test Server Endpoints:")
    print("GET  /              - Server info")
    print("GET  /health        - Health check")
    print("POST /test-upload   - Test file upload")
    print("POST /mock-process  - Full processing mock\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)