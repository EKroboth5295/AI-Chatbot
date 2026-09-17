from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from empathy_engine import EmpathyEngine
from location_service import LocationService
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from voices import VOICE_PROFILES

load_dotenv()

eleven_client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

app = Flask(__name__)
CORS(app)

engine = EmpathyEngine()
locations = LocationService()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    voice_mode = data.get("voice_mode", "neutral")
    user_location = data.get("location")  # Optional: {"lat": ..., "lng": ...}

    if not user_message:
        return jsonify({"reply": "I'm here with you. What's on your mind?"})

    # Detect if user is asking for a calming spot
    spot = None
    if locations.needs_calming_spot(user_message) and user_location:
        spot = locations.find_nearest_calming_spot(user_location)

    reply = engine.respond(user_message, voice_mode, spot)
    return jsonify({
        "reply": reply["text"],
        "tone": reply["tone"],
        "spot": spot
    })


@app.route("/api/locations", methods=["GET"])
def get_locations():
    return jsonify(locations.all_spots())

@app.route("/api/tts", methods=["POST"])
def tts():
    data = request.json
    text = data.get("text", "").strip()
    voice_mode = data.get("voice_mode", "neutral")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    profile = VOICE_PROFILES.get(
        voice_mode,
        VOICE_PROFILES["neutral"]
    )

    voice_id = profile["voice_id"]

    try:
        audio = eleven_client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2"
        )

        audio_bytes = b"".join(audio)

        from flask import Response

        return Response(
            audio_bytes,
            mimetype="audio/mpeg"
        )

    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return jsonify({"error": "TTS failed"}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
