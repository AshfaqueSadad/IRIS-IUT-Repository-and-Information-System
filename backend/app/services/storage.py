import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StorageService:
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER

    async def save_file(self, file: UploadFile) -> str:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        if self.provider == "local" or not settings.S3_ACCESS_KEY_ID:
            file_path = UPLOAD_DIR / unique_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file.file.seek(0)
            return f"{settings.S3_PUBLIC_URL_PREFIX}/{unique_filename}"
        else:
            # S3 / Cloudflare R2 upload using boto3
            import boto3
            s3 = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            )
            s3.upload_fileobj(
                file.file,
                settings.S3_BUCKET_NAME,
                unique_filename,
                ExtraArgs={"ContentType": file.content_type},
            )
            file.file.seek(0)
            return f"{settings.S3_PUBLIC_URL_PREFIX}/{unique_filename}"


storage_service = StorageService()
