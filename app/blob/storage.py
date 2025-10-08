import os
from uuid import uuid4

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.errors import BlobError


def create_bucket():
    client_internal = Minio(
        settings.blob.internal_endpoint,
        access_key=settings.blob.user,
        secret_key=settings.blob.password,
        secure=settings.blob.internal_secure,
    )
    found = client_internal.bucket_exists(settings.blob.bucket)
    if not found:
        client_internal.make_bucket(settings.blob.bucket)


def upload(file_path: str, dest_folder_name: str) -> str:
    client_internal = Minio(
        settings.blob.internal_endpoint,
        access_key=settings.blob.user,
        secret_key=settings.blob.password,
        secure=settings.blob.internal_secure,
    )
    # only public client needs secure since internal is in a secure channel
    client_public = Minio(
        settings.blob.public_endpoint,
        access_key=settings.blob.user,
        secret_key=settings.blob.password,
        secure=settings.blob.public_secure,
    )
    _, file_extension = os.path.splitext(file_path)
    fileId = uuid4().hex
    dest_path = f"{dest_folder_name}/{fileId}{file_extension}"

    try:
        client_internal.fput_object(settings.blob.bucket, dest_path, file_path)
        # pre-signed urls use the public client so they can be accessed from the public endpoint
        return client_public.presigned_get_object(settings.blob.bucket, dest_path)
    except S3Error as err:
        raise BlobError(f"S3 operation failed: {str(err)}") from err


if __name__ == "__main__":
    create_bucket()
