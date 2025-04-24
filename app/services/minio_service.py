import os
import logging
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

def initialize_minio_client():
    return Minio(
        f"{os.environ['MINIO_URL']}:{os.environ['MINIO_PORT']}",
        access_key=os.environ['MINIO_ROOT_USER'],
        secret_key=os.environ['MINIO_ROOT_PASSWORD'],
        secure=False
    )

def postFileInBucket(client, bucket_name, path_dest, path_src, content_type=None):
    if path_src.endswith('.mp4'):
        content_type = 'video/mp4'
    elif path_src.endswith('.mp3'):
        content_type = 'audio/mpeg'
    elif path_src.endswith('.txt'):
        content_type = 'text/plain'

    client.fput_object(bucket_name, path_dest, path_src, content_type=content_type)
    logger.info(f"Arquivo {path_src} enviado para {bucket_name}/{path_dest}")