from flask import Flask, request, send_file, jsonify, render_template
from transformers import AutoProcessor, BarkModel
import scipy
import numpy as np
import os
import replicate
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)

# Initialize Bark models
processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")
default_voice_preset = "v2/en_speaker_6"  # fallback preset

# Configure Replicate client
replicate_client = replicate.Client(api_token="r8_B5Riax1c95EAkwcZFzXiLjds4h1x9Tm43x3OF")

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
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        text = request.form.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, secure_filename(audio_file.filename))
        audio_file.save(audio_path)

        # Process with F5-TTS
        with open(audio_path, "rb") as ref_audio:
            input = {
                "gen_text": text,
                "ref_text": "",  # You can modify this if needed
                "ref_audio": ref_audio
            }

            output = replicate_client.run(
                "x-lance/f5-tts:87faf6dd7a692dd82043f662e76369cab126a2cf1937e25a9d41e0b834fd230e",
                input=input
            )

            # Save the output to a temporary file
            output_path = os.path.join(temp_dir, "cloned_output.wav")
            with open(output_path, "wb") as file:
                file.write(output.read())

            # Clean up the uploaded file
            os.remove(audio_path)

            return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the temporary directory
        if 'temp_dir' in locals():
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error removing temp directory: {e}")

if __name__ == "__main__":
    app.run(debug=True)