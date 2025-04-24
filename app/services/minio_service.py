import os
import logging
import subprocess
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
    ext = os.path.splitext(path_src)[-1].lower()

    if ext == '.mp4':
        content_type = 'video/mp4'
    elif ext == '.mp3':
        content_type = 'audio/mpeg'
    elif ext == '.txt':
        content_type = 'text/plain'

    # Envia o arquivo original
    client.fput_object(bucket_name, path_dest, path_src, content_type=content_type)
    logger.info(f"Arquivo {path_src} enviado para {bucket_name}/{path_dest}")

    # Se for .mp4, converte para .mp3 e envia também
    if ext == '.mp4':
        mp3_path = path_src.replace('.mp4', '.mp3')
        try:
            logger.info(f"Convertendo {path_src} para MP3...")
            subprocess.run([
                "ffmpeg", "-i", path_src, "-vn", "-acodec", "libmp3lame", "-y", mp3_path
            ], check=True)

            mp3_dest = path_dest.replace('.mp4', '.mp3')
            client.fput_object(bucket_name, mp3_dest, mp3_path, content_type='audio/mpeg')
            logger.info(f"Arquivo MP3 {mp3_path} enviado para {bucket_name}/{mp3_dest}")

            # Opcional: remove o .mp3 local após upload
            os.remove(mp3_path)

        except Exception as e:
            logger.error(f"Erro ao converter/upload do MP3: {str(e)}")
