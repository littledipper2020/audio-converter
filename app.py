from flask import Flask, request, send_file, render_template
import subprocess
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + file.filename)
    file.save(input_path)

    original_name = os.path.splitext(file.filename)[0]
    output_filename = f"{original_name}.wav"
    output_path = os.path.join(PROCESSED_FOLDER, output_filename)

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ar", "8000",
        "-ac", "1",
        "-f", "wav",
        "-c:a", "pcm_alaw",
        output_path
    ]
    subprocess.run(command, check=True)

    return send_file(output_path, as_attachment=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's port or default to 10000
    app.run(host="0.0.0.0", port=port)
