from pydantic import BaseModel, Field
from typing import List

class VoiceResponse(BaseModel):
    id: int
    voice_id: str
    name: str
    sample_s3_url: str

    class Config:
        from_attributes = True

class SpeakRequest(BaseModel):
    voice_id: str
    text: str

class SpeakResponse(BaseModel):
    message: str
    generated_speech_s3_url: str
    record_id: int

class TuneSettingsRequest(BaseModel):
    stability: float = Field(0.7, ge=0, le=1)
    similarity_boost: float = Field(0.8, ge=0, le=1)

class TuneSettingsResponse(BaseModel):
    message: str
    voice_id: str
    settings: TuneSettingsRequest

class CloneAndSpeakResponse(BaseModel):
    message: str
    cloned_voice_record_id: int
    generated_speech_record_id: int
    elevenlabs_voice_id: str
    voice_sample_s3_url: str
    generated_speech_s3_url: str

