from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.biometrics.speechbrain_model import identify_speaker, enroll_speaker
from app.ai.gemini_client import get_intent
import os

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/enroll")
async def enroll_user(name: str = Form(...), audio: UploadFile = File(...)):
    """Saves a voiceprint for the user."""
    file_location = f"temp_{name}.wav"
    with open(file_location, "wb") as f:
        f.write(await audio.read())
    
    success = enroll_speaker(name, file_location)
    os.remove(file_location)
    
    if success:
        return {"status": "success", "message": f"User {name} enrolled successfully."}
    raise HTTPException(status_code=500, detail="Failed to enroll user.")

@app.post("/api/command")
async def process_command(text: str = Form(...), audio: UploadFile = File(...)):
    """Identifies the speaker and processes the command intent."""
    file_location = "temp_command.wav"
    with open(file_location, "wb") as f:
        f.write(await audio.read())
        
    # 1. Identify Speaker from Audio
    speaker_name = identify_speaker(file_location)
    os.remove(file_location)
    
    # 2. Get Intent from Gemini
    intent = get_intent(text, speaker_name)
    
    return {"speaker": speaker_name, "intent": intent}