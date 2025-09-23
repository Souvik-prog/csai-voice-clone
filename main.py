# main.py
import os
from app.workflow import run_full_cloning_process
from config import settings

if __name__ == "__main__":
    VOICE_NAME = "My Cloned Voice"
    TEXT_TO_SPEAK = "Hello from my modularized application! This structure is much easier to manage and scale."

    INPUT_SAMPLE_FILENAME = "my_voice_sample.wav" 

    input_file_path = os.path.join(settings.INPUT_SAMPLES_DIR, INPUT_SAMPLE_FILENAME)

    if not os.path.exists(input_file_path):
        print(f"ERROR: Input sample not found at {input_file_path}")
        print("Please place your audio sample in the 'assets/input_samples' directory.")
    else:
        run_full_cloning_process(
            sample_path=input_file_path,
            voice_name=VOICE_NAME,
            text_to_speak=TEXT_TO_SPEAK
        )