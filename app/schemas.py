from pydantic import BaseModel, Field
from typing import Optional

# --- Request Models ---

# ... existing TuneSettingsRequest and GenerateSpeechRequest ...
class TuneSettingsRequest(BaseModel):
    stability: float = Field(0.7, ge=0, le=1, description="Stability of the voice.")
    similarity_boost: float = Field(0.8, ge=0, le=1, description="Similarity boost for the voice.")

class GenerateSpeechRequest(BaseModel):
    voice_id: str = Field(..., description="The ID of the voice to use for generation.")
    text: str = Field(..., min_length=1, description="The text to be converted to speech.")


# --- Response Models ---

class VoiceCloneResponse(BaseModel):
    message: str
    voice_id: str
    sample_s3_url: str
    db_record_id: int

class CloneAndSpeakResponse(BaseModel):
    message: str
    cloned_voice_record_id: int
    generated_speech_record_id: int
    elevenlabs_voice_id: str
    voice_sample_s3_url: str
    generated_speech_s3_url: str

class TuneSettingsRequest(BaseModel):
    stability: float = Field(0.7, ge=0, le=1)
    similarity_boost: float = Field(0.8, ge=0, le=1)

class TuneSettingsResponse(BaseModel):
    message: str
    voice_id: str
    settings: TuneSettingsRequest


class GenerateSpeechResponse(BaseModel):
    message: str
    s3_url: str
    db_record_id: int

