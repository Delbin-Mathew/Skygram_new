from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import google.generativeai as genai
import requests
import re
import os
import uuid
from pathlib import Path
from typing import Dict, Any
import random
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="SkyGram AI Backend", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS (more secure defaults)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# =========================
# Configuration
# =========================
# Get API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not GEMINI_API_KEY or not HF_TOKEN:
    raise ValueError("API keys not found in environment variables")

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model_text = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    logger.error(f"Failed to configure Gemini: {str(e)}")
    raise

# Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Create directories for storing images
UPLOAD_DIR = Path("uploads")
GENERATED_DIR = Path("generated")
UPLOAD_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

# Funny captions
FUNNY_CAPTIONS = [
    "Nature's got jokes! 🌤️",
    "When clouds have better imagination than humans 🤭",
    "Sky doodles by Mother Nature 🎨",
    "Clouds: Nature's abstract artists 🎭",
    "The sky is the limit for cloud creativity ✨",
    "Every cloud has a silver lining... and a funny shape! 😄"
]

# =========================
# Helper Functions
# =========================
def clean_filename(text: str) -> str:
    """Clean text for safe filename usage"""
    return re.sub(r"\W+", "_", text).lower()

def query_huggingface(prompt: str) -> bytes:
    """Query Hugging Face API for image generation"""
    try:
        payload = {"inputs": prompt}
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=502, detail="Image generation service unavailable")
        
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Hugging Face request failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

# =========================
# API Endpoints
# =========================
@app.get("/")
async def root():
    return {"message": "SkyGram AI Backend is running!"}

@app.post("/process-cloud")
async def process_cloud(file: UploadFile = File(...)):
    """Process uploaded cloud image through AI pipeline"""
    # Validate file type and size
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    try:
        session_id = str(uuid.uuid4())
        file_content = await file.read()
        
        # Save original file
        original_path = UPLOAD_DIR / f"{session_id}_original.jpg"
        original_path.write_bytes(file_content)
        logger.info(f"Saved original image: {original_path}")

        # Step 1: Gemini - Identify object in cloud
        try:
            image_data = {"mime_type": file.content_type, "data": file_content}
            prompt_identify = "Reply with only one short noun for what this cloud most resembles. Be creative but keep it simple."
            
            identify_response = model_text.generate_content([prompt_identify, image_data])
            thing_name = identify_response.text.strip().lower()
            clean_name = clean_filename(thing_name)
            logger.info(f"Identified object: {thing_name}")
        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Cloud analysis failed")

        # Step 2: Hugging Face - Generate cloud art
        generation_prompt = (
            f"A beautiful, artistic representation of a {thing_name} "
            "made entirely of fluffy white clouds against a bright blue sky, "
            "photorealistic, high quality, dreamy atmosphere"
        )
        
        generated_image_bytes = query_huggingface(generation_prompt)
        generated_path = GENERATED_DIR / f"{session_id}_{clean_name}.png"
        generated_path.write_bytes(generated_image_bytes)
        logger.info(f"Saved generated image: {generated_path}")

        # Prepare response
        response_data = {
            "session_id": session_id,
            "detected_object": thing_name,
            "caption": random.choice(FUNNY_CAPTIONS),
            "original_image_url": f"/images/original/{session_id}",
            "generated_image_url": f"/images/generated/{session_id}_{clean_name}.png",
            "download_url": f"/download/{session_id}_{clean_name}.png"
        }
        logger.info(f"Response data: {response_data}")
        logger.info(f"Generated image path: {generated_path}")
        logger.info(f"Generated image URL: {response_data['generated_image_url']}")
        return JSONResponse(response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ... (keep your existing endpoint functions for images and download)

@app.get("/images/original/{session_id}")
async def get_original_image(session_id: str):
    """Get original uploaded image"""
    try:
        # Find the original image file
        image_files = list(UPLOAD_DIR.glob(f"{session_id}_original.*"))
        if not image_files:
            raise HTTPException(status_code=404, detail="Original image not found")
        
        image_path = image_files[0]
        return FileResponse(image_path, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error serving original image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error serving image")

@app.get("/images/generated/{filename}")
async def get_generated_image(filename: str):
    """Get generated AI art image"""
    try:
        image_path = GENERATED_DIR / filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Generated image not found")
        
        return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        logger.error(f"Error serving generated image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error serving image")

@app.get("/download/{filename}")
async def download_image(filename: str):
    """Download generated image"""
    try:
        image_path = GENERATED_DIR / filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            image_path, 
            media_type="image/png",
            filename=f"cloud-art-{filename}"
        )
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading image")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "gemini": "configured" if GEMINI_API_KEY else "missing",
            "huggingface": "configured" if HF_TOKEN else "missing"
        },
        "directories": {
            "uploads": str(UPLOAD_DIR),
            "generated": str(GENERATED_DIR)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )