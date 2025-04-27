from flask import Flask, request, send_file, jsonify, render_template
from transformers import AutoProcessor, BarkModel
import scipy
import numpy as np
import os
import replicate
from werkzeug.utils import secure_filename
import tempfile
import requests
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Initialize Bark models
processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")
default_voice_preset = "v2/en_speaker_6"  # fallback preset

# Configure Replicate client
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate")
def generate_page():
    return render_template("generate.html")

@app.route("/clone")
def clone_page():
    return render_template("cloning.html")

@app.route("/api/generate", methods=["POST"])
def generate_audio():
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice_preset = data.get("voice_preset", default_voice_preset)

        if not text.strip():
            return jsonify({"error": "Text is required"}), 400

        inputs = processor(text, voice_preset=voice_preset)
        audio_array = model.generate(**inputs).cpu().numpy().squeeze()
        sample_rate = model.generation_config.sample_rate

        output_path = "output.wav"
        scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

        return send_file(output_path, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clone", methods=["POST"])
def clone_voice():
    audio_file = request.files['audio']
    text = request.form['text']

    audio_path = os.path.join(OUTPUT_DIR, audio_file.filename)
    audio_file.save(audio_path)

    with open(audio_path, "rb") as ref_audio:
        output_url = replicate_client.run(
            "x-lance/f5-tts:87faf6dd7a692dd82043f662e76369cab126a2cf1937e25a9d41e0b834fd230e",
            input={"gen_text": text, "ref_text": "", "ref_audio": ref_audio}
        )

    response = requests.get(output_url)
    cloned_output_path = os.path.join(OUTPUT_DIR, "cloned.wav")
    with open(cloned_output_path, "wb") as f:
        f.write(response.content)

    return send_file(cloned_output_path, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(debug=True)