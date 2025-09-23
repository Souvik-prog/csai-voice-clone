import requests
import os
from config import settings
import mimetypes

class ElevenLabsClient:
    """A client to interact with the ElevenLabs API."""
    
    def __init__(self):
        self._headers = {
            "Accept": "application/json",
            "xi-api-key": settings.API_KEY
        }

    def clone_voice(self, name: str, description: str, audio_file_path: str) -> str | None:
        """Clones a voice and returns the voice_id."""
        url = f"{settings.API_BASE_URL}/voices/add"
        data = {'name': name, 'description': description}

        mime_type, _ = mimetypes.guess_type(audio_file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        files = [('files', (os.path.basename(audio_file_path), open(audio_file_path, 'rb'), mime_type))]
       
        response = requests.post(url, headers=self._headers, data=data, files=files)
        
        if response.status_code == 200:
            return response.json().get('voice_id')
        else:
            print(f"Error cloning voice: {response.status_code}\n{response.text}")
            return None

    def tune_voice_settings(self, voice_id: str, stability: float, similarity_boost: float):
        """Tunes the settings for a given voice_id."""
        url = f"{settings.API_BASE_URL}/voices/{voice_id}/settings/edit"
        json_data = {"stability": stability, "similarity_boost": similarity_boost}
        headers = self._headers.copy()
        headers["Content-Type"] = "application/json"
        
        response = requests.post(url, json=json_data, headers=headers)
        
        if response.status_code != 200:
            print(f"Error tuning voice: {response.status_code}\n{response.text}")

    def generate_speech(self, voice_id: str, text: str) -> bytes | None:
        """Generates speech audio data (bytes) for the given text and voice_id."""
        url = f"{settings.API_BASE_URL}/text-to-speech/{voice_id}"
        json_data = {
            "text": text,
            "model_id": settings.DEFAULT_MODEL_ID,
            "voice_settings": {
                "stability": settings.DEFAULT_STABILITY,
                "similarity_boost": settings.DEFAULT_SIMILARITY_BOOST
            }
        }
        headers = self._headers.copy()
        headers["Accept"] = "audio/mpeg"
        headers["Content-Type"] = "application/json"
        
        response = requests.post(url, json=json_data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error generating speech: {response.status_code}\n{response.text}")
            return None

elevenlabs_client = ElevenLabsClient()