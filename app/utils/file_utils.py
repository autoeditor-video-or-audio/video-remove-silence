import os

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def remove_temp_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)