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
    files = request.files.getlist("file")
    if not files:
        return "No files uploaded", 400

    processed_files = []

    for file in files:
        if file.filename == "":
            continue

        input_filename = f"{uuid.uuid4()}_{file.filename}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        file.save(input_path)

        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.wav"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        # <--- Replace the command here with the normalization command:
        command = [
            "ffmpeg",
            "-i", input_path,
            "-af", "loudnorm",
            "-ar", "8000",
            "-ac", "1",
            "-f", "wav",
            "-c:a", "pcm_alaw",
            output_path
        ]

        subprocess.run(command, check=True)
        processed_files.append((output_filename, output_path))

    # Rest of your code that sends files back (single file or zipped multiple)...

    # If one file: send it directly
    if len(output_paths) == 1:
        return send_file(output_paths[0], as_attachment=True)

    # If multiple files: zip them for download
    zip_filename = os.path.join(PROCESSED_FOLDER, "converted_files.zip")
    with ZipFile(zip_filename, 'w') as zipf:
        for path in output_paths:
            zipf.write(path, os.path.basename(path))

    return send_file(zip_filename, as_attachment=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
