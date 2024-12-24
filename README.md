
# Video Editor - Remove Silence

[![GitHub Repository](https://img.shields.io/badge/repo-github.com/didevlab/video--editor--remove--silence-blue)](https://github.com/didevlab/video-remove-silence)

This project provides a Python-based video editor that automatically removes silence from video files stored in a MinIO bucket. Leveraging `auto-editor`, the program downloads MP4 files from the specified MinIO bucket, processes them to remove silent segments, and then uploads the processed video back to a designated subfolder in the bucket. All files are removed from both the bucket and local storage after processing to maintain cleanliness.

## Features

- **Automated Silence Removal**: Uses `auto-editor` to detect and remove silent sections from video files.
- **MinIO Integration**: Downloads and uploads MP4 files from/to MinIO, handling bucket organization and cleanup.
- **Environment Configurations**: Key settings, including silence margin, can be configured through environment variables.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/didevlab/video-remove-silence.git
   cd video-remove-silence
   ```

2. **Setup Docker Environment**:
   Ensure Docker is installed and running, then build and run the Docker container using the provided `Dockerfile`.

3. **Dockerfile Example**:
   ```dockerfile
   FROM python:3.9.18-bullseye

   RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
   RUN python -m pip install --upgrade pip

   # Install required packages
   RUN pip3 install setuptools moviepy datetime numpy==1.24
   RUN pip3 install auto-editor
   RUN pip3 install minio requests

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY ./app/ .

   # Optional Entrypoint
   # ENTRYPOINT ["python3", "run.py"]
   ```

## Environment Variables

The following environment variables are used to configure the application:

- **MINIO_URL**: The URL for the MinIO server.
- **MINIO_PORT**: Port number for MinIO.
- **MINIO_ROOT_USER**: Username for MinIO authentication.
- **MINIO_ROOT_PASSWORD**: Password for MinIO authentication.
- **AUTO_EDITOR_MARGIN**: Sets the silence margin for `auto-editor`. Default is `"0.04sec"` if not provided.
- **currentAction**: Timestamp for naming files uniquely during processing.

## Running the Application

You can run the application with Docker or directly with Python:

### Running with Docker
1. **Build the Docker Image**:
   ```bash
   docker build -t video-remove-silence .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -e MINIO_URL=<your_minio_url>               -e MINIO_PORT=<your_minio_port>               -e MINIO_ROOT_USER=<your_minio_user>               -e MINIO_ROOT_PASSWORD=<your_minio_password>               -e AUTO_EDITOR_MARGIN="0.04sec"               video-remove-silence
   ```

### Running Locally
1. **Install Dependencies**:
   Install Python dependencies directly from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Script**:
   Execute the main script:
   ```bash
   python3 run.py
   ```

## Requirements

- Python 3.9+
- FFmpeg
- auto-editor
- MinIO server

## Cleaning Up

Processed files are removed both from the MinIO bucket and local storage after successful processing, keeping the system clutter-free.

## License

This project is licensed under the MIT License.