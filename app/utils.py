import os
from config import settings

def save_audio_file(audio_data: bytes, filename: str) -> str:
    """Saves audio data to a file in the generated_speech directory."""
    os.makedirs(settings.GENERATED_SPEECH_DIR, exist_ok=True)
    
    output_path = os.path.join(settings.GENERATED_SPEECH_DIR, filename)
    
    with open(output_path, 'wb') as f:
        f.write(audio_data)
        
    return output_path