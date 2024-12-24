import os
import subprocess
import shutil
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import numpy as np
import moviepy.editor as mp
from moviepy.editor import AudioFileClip, VideoClip
from utils import green, logger, getListHashTag, getDataFile, sendNotification, removeFolder

current_datetime = datetime.now()
currentAction = current_datetime.strftime("%d-%m-%Y--%H-%M-%S")

def postFileInBucket(client, bucketSet, pathDest, pathSrc, contentType=None):
    if pathSrc[len(pathSrc)-3:len(pathSrc)] == 'txt':
        contentType = 'text/plain'
    logger.debug(green("Fazendo upload no bucket " + bucketSet + " arquivo " + pathDest))
    client.fput_object(
        bucketSet,
        pathDest,
        pathSrc,
        content_type=contentType
    )
    logger.debug(green("Upload do arquivo " + pathSrc + " realizado com sucesso."))

def delete_file_from_bucket(client, bucket_name, object_name):
    """Deleta o arquivo especificado do bucket no MinIO."""
    try:
        client.remove_object(bucket_name, object_name)
        logger.debug(green(f"Arquivo {object_name} deletado com sucesso do bucket {bucket_name}."))
    except S3Error as exc:
        logger.debug(green(f"Erro ao tentar deletar {object_name} do bucket {bucket_name}: {exc}"))

def delete_local_files(*file_paths):
    """Deleta arquivos locais se existirem."""
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(green(f"Arquivo local {file_path} deletado com sucesso."))
        else:
            logger.debug(green(f"Arquivo local {file_path} não encontrado para deletar."))

def download_latest_mp4(client, bucket_name, download_name):
    try:
        # Listar arquivos no bucket e filtrar apenas arquivos MP4 no diretório principal
        objects = client.list_objects(bucket_name, recursive=False)  # Não inclui subdiretórios
        mp4_files = [obj for obj in objects if obj.object_name.endswith('.mp4') and '/' not in obj.object_name]

        # Verifica se há arquivos MP4 no diretório principal do bucket
        if not mp4_files:
            logger.debug(green("Nenhum arquivo MP4 encontrado no diretório principal do bucket autoeditor."))
            return None, None

        # Encontrar o último arquivo pelo atributo 'last_modified'
        latest_file = max(mp4_files, key=lambda obj: obj.last_modified)
        
        # Caminho local com o novo nome definido por currentAction
        local_path = f"./foredit/{download_name}.mp4"

        # Download do último arquivo MP4 com o novo nome
        client.fget_object(bucket_name, latest_file.object_name, local_path)
        logger.debug(green(f"Download do arquivo {latest_file.object_name} realizado com sucesso como {download_name}.mp4"))
        
        return local_path, latest_file.object_name  # Retorna o caminho local e o nome do arquivo no bucket

    except S3Error as exc:
        logger.debug(green("Erro ao acessar o MinIO.", exc))
        return None, None

def process_video(file_path, output_dir):
    # Extraindo o nome do arquivo sem o diretório
    name_processed_file = os.path.basename(file_path)
    
    # Caminho de saída para o arquivo editado
    output_file_path = os.path.join(output_dir, f"WithoutSilence-{name_processed_file}")

    # Lê o valor da margem do ambiente, com padrão para "0.04sec" caso não esteja definido
    margin = os.getenv("AUTO_EDITOR_MARGIN", "0.04sec")

    # Executando o auto-editor com a margem configurada
    subprocess.run([
        "auto-editor",
        file_path,
        "--margin", margin,
        "-o", output_file_path
    ])
    logger.debug(green(f"Processamento do arquivo {name_processed_file} concluído com sucesso com margem {margin}."))
    
    return output_file_path  # Retorna o caminho do arquivo editado

def main():
    MINIO_URL = os.environ['MINIO_URL']
    MINIO_PORT = os.environ['MINIO_PORT']
    MINIO_ROOT_USER = os.environ['MINIO_ROOT_USER']
    MINIO_ROOT_PASSWORD = os.environ['MINIO_ROOT_PASSWORD']
    bucketSet = "autoeditor"
    path_dir_files_edited = "./edited_files/"

    # Criar o diretório de saída se não existir
    os.makedirs(path_dir_files_edited, exist_ok=True)

    client = Minio(
        MINIO_URL + ":" + MINIO_PORT,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=False,
    )  
    logger.debug(green('...START -> ' + str(currentAction)))

    # Chama a função para baixar o último arquivo MP4 com o nome definido por currentAction
    downloaded_file, original_object_name = download_latest_mp4(client, bucketSet, currentAction)
    if downloaded_file:
        logger.debug(green(f"Arquivo baixado em: {downloaded_file}"))
        
        # Processa o vídeo para remover o silêncio
        edited_file = process_video(downloaded_file, path_dir_files_edited)

        # Caminho no bucket para upload do arquivo processado
        upload_path = f"files-without-silence/{os.path.basename(edited_file)}"
        
        # Fazer upload do arquivo editado para o MinIO
        postFileInBucket(client, bucketSet, upload_path, edited_file)

        # Deletar o arquivo original do bucket após o upload bem-sucedido
        if original_object_name:
            delete_file_from_bucket(client, bucketSet, original_object_name)

        # Deletar os arquivos locais (baixado e editado)
        delete_local_files(downloaded_file, edited_file)
    else:
        logger.debug(green("Nenhum arquivo foi baixado."))

    logger.debug(green('...FINISHED...'))

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        logger.debug(green("Erro ocorrido.", exc))
