import subprocess
from config import AUTO_EDITOR_MARGIN, AUTO_EDITOR_FRAME_MARGIN

def remove_silence(filepath, output_path):
    subprocess.run([
        "auto-editor", filepath,
        "--margin", AUTO_EDITOR_MARGIN,
        "-o", output_path
    ])
        # "--frame-margin", AUTO_EDITOR_FRAME_MARGIN,