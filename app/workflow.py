from sqlalchemy.orm import Session
from .api_client import elevenlabs_client
from .s3_handler import upload_audio_to_s3
from . import models
import uuid
from typing import Tuple

def run_full_voice_processing_workflow(
    db: Session,
    voice_name: str,
    voice_description: str,
    temp_file_path: str,
    original_filename: str,
    text_to_speak: str
) -> Tuple[models.ClonedVoice, models.GeneratedSpeech] | None:
    """
    Orchestrates the entire process:
    1. Uploads voice sample to S3.
    2. Clones the voice via ElevenLabs.
    3. Stores the cloned voice record in DB.
    4. Generates speech from the new voice.
    5. Uploads generated speech to S3.
    6. Stores the generated speech record in DB.
    """
    # === Step 1: Handle the Input Voice Sample ===
    print(f"Uploading voice sample '{original_filename}' to S3.")
    with open(temp_file_path, "rb") as f:
        sample_audio_data = f.read()
    
    sample_object_name = f"voice-samples/{uuid.uuid4()}-{original_filename}"
    sample_s3_url = upload_audio_to_s3(sample_audio_data, sample_object_name)
    if not sample_s3_url:
        print("Failed to upload voice sample to S3.")
        return None

    # === Step 2: Clone the Voice ===
    print(f"Cloning voice '{voice_name}' using the sample.")
    voice_id = elevenlabs_client.clone_voice(voice_name, voice_description, temp_file_path)
    if not voice_id:
        print("Failed to clone voice via ElevenLabs API.")
        return None

    # === Step 3: Store the Cloned Voice Record ===
    cloned_voice_record = models.ClonedVoice(
        voice_id=voice_id, name=voice_name, description=voice_description, sample_s3_url=sample_s3_url
    )
    db.add(cloned_voice_record)
    db.commit()
    db.refresh(cloned_voice_record)
    print(f"Stored cloned voice record with ID: {cloned_voice_record.id}")

    # === Step 4: Generate Speech with the New Voice ===
    print(f"Generating speech for text: '{text_to_speak[:40]}...'")
    generated_audio_data = elevenlabs_client.generate_speech(voice_id, text_to_speak)
    if not generated_audio_data:
        print("Failed to generate speech audio.")
        return None

    # === Step 5: Upload Generated Speech to S3 ===
    generated_object_name = f"speech-outputs/{voice_id}/{uuid.uuid4()}.mp3"
    generated_s3_url = upload_audio_to_s3(generated_audio_data, generated_object_name)
    if not generated_s3_url:
        print("Failed to upload generated speech to S3.")
        return None

    # === Step 6: Store the Generated Speech Record ===
    generated_speech_record = models.GeneratedSpeech(
        text_content=text_to_speak, s3_url=generated_s3_url, source_voice=cloned_voice_record
    )
    db.add(generated_speech_record)
    db.commit()
    db.refresh(generated_speech_record)
    print(f"Stored generated speech record with ID: {generated_speech_record.id}")

    return (cloned_voice_record, generated_speech_record)

