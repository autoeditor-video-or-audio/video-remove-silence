FROM python:3.9.18-bullseye

# Install os dependencies
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends libmediainfo0v5 libmediainfo-dev ffmpeg
RUN python -m pip install --upgrade pip

COPY requirements.txt .
# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./app/ .

# ENTRYPOINT ["bash"]
# ENTRYPOINT ["python3", "run.py"]

# docker build -t video-remove-silence .
# docker rm -f pod && docker run -ti --name pod -v ./app:/app/ --env-file env.list video-remove-silence bash