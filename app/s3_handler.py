import boto3
from botocore.exceptions import NoCredentialsError
import os
from config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def upload_audio_to_s3(audio_data: bytes, object_name: str) -> str | None:
    """
    Uploads audio data (bytes) to an S3 bucket and returns the public URL.
    """
    try:
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=object_name,
            Body=audio_data,
            ContentType='audio/mpeg'
        )
        # Construct the URL
        url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        print(f"Successfully uploaded to S3. URL: {url}")
        return url
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return None
    except Exception as e:
        print(f"An error occurred during S3 upload: {e}")
        return None
