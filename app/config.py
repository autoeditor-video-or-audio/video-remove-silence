import os

WORK_DIR = "/app/videocast/"
BUCKET_NAME = os.getenv("BUCKET_NAME", "audiocast")
NOSILENCE_PREFIX = os.getenv("NOSILENCE_PREFIX", "nosilence")
QUEUE_OUTPUT = os.getenv("QUEUE_OUTPUT", "01_audiocast")
AUTO_EDITOR_MARGIN = os.getenv("AUTO_EDITOR_MARGIN", "0.1sec,0.2sec")
AUTO_EDITOR_FRAME_MARGIN = os.getenv("AUTO_EDITOR_FRAME_MARGIN", "6")
