from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class ClonedVoice(Base):
    __tablename__ = "cloned_voices"

    id = Column(Integer, primary_key=True, index=True)
    voice_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    sample_s3_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This creates the relationship to the generated speech records
    generated_speech = relationship("GeneratedSpeech", back_populates="source_voice")

class GeneratedSpeech(Base):
    __tablename__ = "generated_speech"

    id = Column(Integer, primary_key=True, index=True)
    text_content = Column(String)
    s3_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign key to link back to the ClonedVoice table
    cloned_voice_id = Column(Integer, ForeignKey("cloned_voices.id"))
    
    source_voice = relationship("ClonedVoice", back_populates="generated_speech")

