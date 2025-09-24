from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Import the CORS middleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid

from app.database import engine, get_db
from app import models, schemas, workflow
from app.api_client import elevenlabs_client
from config import settings
from app.s3_handler import upload_audio_to_s3


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voice Cloning API",
    description="An API for cloning voices, tuning them, and generating speech.",
    version="2.1.0"
)

# --- CORS Middleware Configuration ---
# This allows your frontend (running on a different port) to communicate with this backend.
origins = [
    "http://localhost",
    "http://localhost:3008", # Add the port your frontend is running on
    "http://127.0.0.1:3008",
    "null", # This can be useful for local file:// testing
    # Add any other origins you might use for development or production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


# --- NEW ENDPOINT to get all cloned voices ---
@app.get("/voices/", response_model=List[schemas.VoiceResponse])
async def get_all_voices(db: Session = Depends(get_db)):
    """
    Retrieves a list of all cloned voices from the database.
    """
    voices = db.query(models.ClonedVoice).all()
    return voices

# --- NEW ENDPOINT to generate speech from an existing voice ---
@app.post("/speak/", response_model=schemas.SpeakResponse)
async def speak_with_existing_voice(
    payload: schemas.SpeakRequest,
    db: Session = Depends(get_db)
):
    """
    Generates speech using a previously cloned voice.
    """
    # 1. Find the corresponding voice record in the database
    voice_record = db.query(models.ClonedVoice).filter(models.ClonedVoice.voice_id == payload.voice_id).first()
    if not voice_record:
        raise HTTPException(status_code=404, detail=f"Voice with ID '{payload.voice_id}' not found.")

    # 2. Generate the audio using ElevenLabs client
    print(f"Generating speech for voice ID {payload.voice_id}...")
    audio_data = elevenlabs_client.generate_speech(payload.voice_id, payload.text)
    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate audio from ElevenLabs.")

    # 3. Upload the generated audio to S3
    s3_object_name = f"speech-outputs/{payload.voice_id}/{uuid.uuid4()}.mp3"
    s3_url = upload_audio_to_s3(audio_data, s3_object_name)
    if not s3_url:
        raise HTTPException(status_code=500, detail="Failed to upload generated audio to S3.")

    # 4. Save the record in the database
    speech_record = models.GeneratedSpeech(
        text_content=payload.text,
        s3_url=s3_url,
        source_voice=voice_record
    )
    db.add(speech_record)
    db.commit()
    db.refresh(speech_record)

    return {
        "message": "Speech generated successfully.",
        "generated_speech_s3_url": s3_url,
        "record_id": speech_record.id
    }


# --- Existing Endpoints ---
@app.post("/clone-and-speak/", response_model=schemas.CloneAndSpeakResponse)
async def clone_and_speak_api(
    db: Session = Depends(get_db),
    voice_name: str = Form(...),
    text_to_speak: str = Form(...),
    voice_description: str = Form(""),
    file: UploadFile = File(...)
):
    # This endpoint remains the same
    os.makedirs(settings.INPUT_SAMPLES_DIR, exist_ok=True)
    temp_path = os.path.join(settings.INPUT_SAMPLES_DIR, file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = workflow.run_full_voice_processing_workflow(
        db=db,
        voice_name=voice_name,
        voice_description=voice_description,
        temp_file_path=temp_path,
        original_filename=file.filename,
        text_to_speak=text_to_speak
    )

    os.remove(temp_path)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to complete the voice processing workflow.")

    cloned_voice_record, generated_speech_record = result

    return {
        "message": "Voice processed successfully.",
        "cloned_voice_record_id": cloned_voice_record.id,
        "generated_speech_record_id": generated_speech_record.id,
        "elevenlabs_voice_id": cloned_voice_record.voice_id,
        "voice_sample_s3_url": cloned_voice_record.sample_s3_url,
        "generated_speech_s3_url": generated_speech_record.s3_url,
    }

@app.post("/tune/{voice_id}", response_model=schemas.TuneSettingsResponse)
async def tune_voice_api(voice_id: str, settings: schemas.TuneSettingsRequest):
    elevenlabs_client.tune_voice_settings(
        voice_id, settings.stability, settings.similarity_boost
    )
    return {
        "message": f"Settings for voice {voice_id} updated.",
        "voice_id": voice_id,
        "settings": settings
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Voice Cloning API v2. Visit /docs for documentation."}

