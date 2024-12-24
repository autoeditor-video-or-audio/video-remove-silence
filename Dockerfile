FROM python:3.9.18-bullseye

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
RUN python -m pip install --upgrade pip

##VIDEO
# RUN pip3 install setuptools moviepy datetime numpy==1.24

##EDIT VIDEO
# RUN pip3 install auto-editor

## MINIO REQUESTS
# RUN pip3 install minio requests

COPY requirements.txt .
# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./app/ .


# ENTRYPOINT ["bash"]
# ENTRYPOINT ["python3", "run.py"]