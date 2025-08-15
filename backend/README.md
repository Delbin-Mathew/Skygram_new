# SkyGram AI Backend

FastAPI backend for cloud shape recognition and AI art generation.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /process-cloud` - Upload and process cloud image
- `GET /images/original/{session_id}` - Get original uploaded image
- `GET /images/generated/{filename}` - Get generated cloud art
- `GET /download/{filename}` - Download generated image
- `GET /health` - Health check

## API Keys Required

1. **Gemini API Key**: Get from https://aistudio.google.com/app/apikey
2. **Hugging Face Token**: Get from https://huggingface.co/settings/tokens

## Deployment

Deploy to Render, Railway, or any Python hosting service. Make sure to:
1. Set environment variables for API keys
2. Update CORS origins for your frontend domain
3. Update the `API_BASE_URL` in the frontend