from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.database import engine, get_db
from app import models, schemas, workflow
from app.api_client import elevenlabs_client
from config import settings

# This will now create/update the tables in your PostgreSQL database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voice Cloning API",
    description="An API for cloning voices, tuning them, and generating speech.",
    version="2.0.0" # Version bump!
)

@app.post("/clone-and-speak/", response_model=schemas.CloneAndSpeakResponse)
async def clone_and_speak_api(
    db: Session = Depends(get_db),
    voice_name: str = Form(...),
    text_to_speak: str = Form(...),
    voice_description: str = Form(""),
    file: UploadFile = File(...)
):
    """
    A single endpoint to perform the entire voice processing pipeline:
    1. Uploads a voice sample and saves it to S3.
    2. Clones the voice.
    3. Generates new speech using that voice.
    4. Saves the generated speech to S3.
    5. Stores records for both actions in the database.
    """
    # Save the uploaded file temporarily to pass its path to the workflow
    os.makedirs(settings.INPUT_SAMPLES_DIR, exist_ok=True)
    temp_path = os.path.join(settings.INPUT_SAMPLES_DIR, file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Execute the entire workflow
    result = workflow.run_full_voice_processing_workflow(
        db=db,
        voice_name=voice_name,
        voice_description=voice_description,
        temp_file_path=temp_path,
        original_filename=file.filename,
        text_to_speak=text_to_speak
    )

    os.remove(temp_path)  # Clean up the temporary file

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
    """
    Fine-tunes the settings for a specific voice. (This endpoint remains useful).
    """
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

