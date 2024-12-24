from os.path import abspath, join, dirname
import os
import logging
import requests
import shutil

## Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s %(message)s',
    datefmt='[%H:%M:%S]'
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

"""
Utilities for TikTok Uploader
"""

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def bold(to_bold: str) -> str:
    """
    Returns the input bolded
    """
    return BOLD + to_bold + ENDC

def green(to_green: str) -> str:
    """
    Returns the input green
    """
    return OKGREEN + to_green + ENDC


def getListHashTag(filePath) -> list:
    logger.debug(green(str('Convertendo arquivo ' + filePath + ' em uma list de hashtags.')))
    with open(filePath, 'r') as file:
    # Lê as linhas do arquivo
      content = file.read().strip()
      file.close()

    # Separa as hashtags por um espaço em branco e cria uma lista de hashtags
    hashtags_list = content.split(' ')

    hashtags_list = [hashtag.lstrip('#') for hashtag in hashtags_list]

    # Exibe a lista de hashtags
    logger.debug(green('Lista de hashtags: ' + str(hashtags_list)))
    return hashtags_list


def getDataFile(filePath):
    logger.debug(green(str('Lendo conteúdo do arquivo ' + filePath)))
    # Abre o arquivo em modo de leitura
    with open(filePath, 'r') as file:
      # Lê as linhas do arquivo
      content = file.read()
      file.close()
    logger.debug(green('Conteúdo: ' + str(content)))
    return content

def sendNotification(urlApprise, title, message):
  payload = {
    'title': title,
    'body': message,
  }
  # The Request
  response = response = requests.post(urlApprise, data=payload)
  if response.status_code == 200:
    logger.debug(green('Send telegram msg: ' + message))


def removeFolder(folderForDeleted):
  # Verifica se o caminho existe e se é uma pasta
  if os.path.exists(folderForDeleted) and os.path.isdir(folderForDeleted):
      try:
          # Remove a pasta e todo o seu conteúdo
          shutil.rmtree(folderForDeleted)
          print(f"A pasta {folderForDeleted} e seu conteúdo foram removidos com sucesso.")
      except OSError as e:
          print(f"Erro: {e.filename} - {e.strerror}.")
  else:
      print(f"O caminho {folderForDeleted} não existe ou não é uma pasta.")


def verificar_extensao_arquivo(caminho_arquivo, exte):
    _, extensao = os.path.splitext(caminho_arquivo)
    extensao = extensao.lower()  # Converte para minúsculas para lidar com extensões como .MP3 ou .MP4
    if extensao == exte:
        return True
    else:
        return False

def createDir(diretorio):  
    pathDirFilesEdited = diretorio
    try:
      os.makedirs(pathDirFilesEdited)
      logger.debug(green(f'Diretório {pathDirFilesEdited} criado com sucesso!'))
    except FileExistsError:
      logger.debug(green(f'Diretório {pathDirFilesEdited} já existe.'))    