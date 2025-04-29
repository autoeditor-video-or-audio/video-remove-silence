import os
import json
import logging
import subprocess
from datetime import datetime
from services.minio_service import initialize_minio_client, postFileInBucket
from config import WORK_DIR, BUCKET_NAME, NOSILENCE_PREFIX, QUEUE_OUTPUT
from utils.file_utils import create_directory, remove_temp_files
from services.silence_remover import remove_silence
import pika

logger = logging.getLogger(__name__)

def get_video_resolution(file_path):
    try:
        # Chama ffprobe para pegar a resolução
        result = subprocess.run(
            [
                'ffprobe', 
                '-v', 'error', 
                '-select_streams', 'v:0', 
                '-show_entries', 'stream=width,height', 
                '-of', 'json', 
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Erro ao obter resolução: {result.stderr}")
            return None, None

        info = json.loads(result.stdout)
        streams = info.get('streams', [])
        if not streams:
            return None, None

        width = streams[0].get('width')
        height = streams[0].get('height')
        return width, height

    except Exception as e:
        logger.error(f"Erro ao extrair resolução do vídeo: {e}")
        return None, None

def publish_result(message):
    try:
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', ''),
            os.getenv('RABBITMQ_PASS', '')
        )
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', ''),
            port=int(os.getenv('RABBITMQ_PORT', 5672)),
            virtual_host=os.getenv('RABBITMQ_VHOST', '/'),
            credentials=credentials
        ))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_OUTPUT, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_OUTPUT,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info("Mensagem publicada com sucesso.")
        connection.close()
    except Exception as e:
        logger.error(f"Erro ao publicar no RabbitMQ: {e}")

def process_video_payload(message):
    try:
        filename = message.get("filename")
        subdir = message.get("subdir")

        if not filename or not subdir:
            logger.error("Payload inválido. filename e subdir são obrigatórios.")
            return

        create_directory(WORK_DIR)
        client = initialize_minio_client()

        local_path = os.path.join(WORK_DIR, filename)
        output_path = os.path.join(WORK_DIR, f"nosilence-{filename}")
        remote_path = f"{NOSILENCE_PREFIX}/{filename}"

        logger.info(f"Baixando {subdir}/{filename}")
        client.fget_object(BUCKET_NAME, f"{subdir}/{filename}", local_path)

        logger.info("Removendo silêncio...")
        remove_silence(local_path, output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error("Erro: arquivo de saída não gerado.")
            return

        # Identifica extensão do arquivo
        ext = os.path.splitext(filename)[1].lower()

        # Se for áudio (.mp3, .wav, etc.)
        if ext in ['.mp3', '.wav', '.ogg', '.flac']:
            resolution = None
            layout = "square"
        else:
            # Se for vídeo, pega a resolução
            width, height = get_video_resolution(output_path)
            if width is None or height is None:
                resolution = None
                layout = None
            else:
                resolution = f"{width}x{height}"
                layout = "horizontal" if width >= height else "vertical"

        # Faz o upload para o MinIO
        postFileInBucket(client, BUCKET_NAME, remote_path, output_path)

        # Cria a mensagem com campos adicionais
        result_message = {
            "filename": filename,
            "bucket_path": remote_path,
            "process_no_silence_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resolution": resolution,
            "layout": layout
        }

        publish_result(result_message)

        try:
            client.remove_object(BUCKET_NAME, f"{subdir}/{filename}")
            logger.info(f"Removido do bucket: {subdir}/{filename}")
        except Exception as e:
            logger.warning(f"Erro ao deletar original: {e}")

        remove_temp_files(local_path, output_path)

    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}")
