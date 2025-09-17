from flask import Flask, request, send_file, render_template
import subprocess
import os
import uuid
import zipfile
import io

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

        # 🔊 Normalize and convert
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

# 🗂 Send single file directly or zip multiple
if len(processed_files) == 1:
    original_name = os.path.splitext(processed_files[0][0])[0]
    converted_name = f"{original_name}.wav"
    return send_file(
        processed_files[0][1],
        as_attachment=True,
        download_name=converted_name  # ✅ keeps correct filename
    )

# If multiple, zip them
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    for filename, path in processed_files:
        zip_file.write(path, arcname=filename)
zip_buffer.seek(0)

return send_file(
    zip_buffer,
    as_attachment=True,
    download_name="converted_files.zip",
    mimetype="application/zip"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
