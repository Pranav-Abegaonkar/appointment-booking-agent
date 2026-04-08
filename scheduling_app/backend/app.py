import os
import jwt
import time
import requests
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEOSDK_API_KEY = os.getenv("VIDEOSDK_API_KEY")
VIDEOSDK_SECRET_KEY = os.getenv("VIDEOSDK_SECRET_KEY")

def generate_token():
    """Generates a VideoSDK authentication token."""
    payload = {
        "apikey": VIDEOSDK_API_KEY,
        "permissions": ["allow_join", "allow_mod"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400, # 24-hour expiration
    }
    return jwt.encode(payload, VIDEOSDK_SECRET_KEY, algorithm="HS256")

@app.get("/get-token")
async def get_token():
    """Endpoint for frontend to fetch VideoSDK token."""
    try:
        token = generate_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-room")
async def create_room():
    """Endpoint to create a new VideoSDK room."""
    token = generate_token()
    url = "https://api.videosdk.live/v2/rooms"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

import subprocess
import signal
from fastapi import FastAPI, HTTPException, BackgroundTasks

@app.post("/start-agent")
async def start_agent(room_id: str, background_tasks: BackgroundTasks):
    """Endpoint to trigger the AI agent for a specific room."""
    try:
        # Load environment variables from the agent folder's .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), "..", "agent", ".env")
        # Check if the .env exists in the alternate root as well
        if not os.path.exists(dotenv_path):
             dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
             
        load_dotenv(dotenv_path=dotenv_path)

        # Preparing the environment for the subprocess
        env = os.environ.copy()
        env["VIDEOSDK_ROOM_ID"] = room_id
        
        # Ensure critical keys are passed through
        keys = ["SARVAMAI_API_KEY", "GOOGLE_API_KEY", "CARTESIA_API_KEY", "VIDEOSDK_API_KEY", "VIDEOSDK_SECRET_KEY", "ZAPIER_MCP_API_KEY"]
        for key in keys:
            val = os.getenv(key)
            if val:
                env[key] = val
            else:
                logging.warning(f"Key {key} not found in environment or {dotenv_path}")

        # Path to YOUR working agent script
        agent_path = os.path.join(os.path.dirname(__file__), "..", "agent", "agent.py")
        
        def run_agent():
            # Using the same interpreter as the current process (venv)
            import sys
            subprocess.run([sys.executable, agent_path], env=env)

        background_tasks.add_task(run_agent)
        
        return {"success": True, "message": f"Agent joining room: {room_id}"}
    except Exception as e:
        logging.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
