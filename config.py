import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    """Holds all application configuration."""
    API_KEY = os.getenv("ELEVENLABS_API_KEY")
    API_BASE_URL = "https://api.elevenlabs.io/v1"

    # S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Default voice settings
    DEFAULT_STABILITY = 0.6
    DEFAULT_SIMILARITY_BOOST = 0.85
    DEFAULT_MODEL_ID = "eleven_multilingual_v2" # Added this line to fix the error

    # Directory paths for temporary storage
    INPUT_SAMPLES_DIR = os.path.join("assets", "input_samples")


# Create an instance of the config
settings = Config()

# Basic validation to ensure required variables are loaded
if not all([
    settings.API_KEY,
    settings.AWS_ACCESS_KEY_ID,
    settings.AWS_SECRET_ACCESS_KEY,
    settings.AWS_S3_BUCKET_NAME,
    settings.AWS_REGION,
    settings.DATABASE_URL
]):
    raise ValueError("One or more required environment variables are not set in the .env file.")

