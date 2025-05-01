import os
from flask import Flask, request, jsonify, Response
from threading import Thread
from services.main_worker import process_video_payload
from services.minio_service import initialize_minio_client
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    filename = data.get("filename")
    subdir = data.get("subdir")
    telegramChatId = data.get("telegramChatId")

    if not filename or not subdir or not telegramChatId:
        return Response(
            json.dumps({"status": "error", "message": "Campos 'filename', 'subdir' e 'telegramChatId' são obrigatórios."}, ensure_ascii=False),
            mimetype='application/json',
            status=400
        )

    client = initialize_minio_client()
    bucket_name = os.getenv("BUCKET_NAME", "audiocast")
    object_path = f"{subdir}/{filename}"

    try:
        client.stat_object(bucket_name, object_path)
    except Exception:
        return Response(
            json.dumps({
                "status": "error",
                "message": f"O arquivo '{object_path}' não existe no bucket '{bucket_name}'."
            }, ensure_ascii=False),
            mimetype='application/json',
            status=404
        )

    def background_task(payload):
        process_video_payload(payload)

    Thread(target=background_task, args=({"filename": filename, "subdir": subdir, "telegramChatId": telegramChatId},)).start()

    return Response(
        json.dumps({"status": "processing", "message": f"Iniciado para {filename}"}, ensure_ascii=False),
        mimetype='application/json',
        status=202
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)