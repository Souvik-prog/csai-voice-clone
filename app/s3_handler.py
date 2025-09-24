import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import io
from config import settings

def upload_audio_to_s3(audio_data: bytes, object_name: str) -> str | None:

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    try:
        audio_stream = io.BytesIO(audio_data)
        
        s3_client.upload_fileobj(
            audio_stream,
            settings.AWS_S3_BUCKET_NAME,
            object_name,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'audio/mpeg'
            }
        )

        url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        print(f"Successfully uploaded to S3. Public URL: {url}")
        return url

    except (NoCredentialsError, PartialCredentialsError):
        print("S3 credentials not available. Please configure them in your .env file.")
        return None
    except Exception as e:
        print(f"An error occurred during S3 upload: {e}")
        return None

