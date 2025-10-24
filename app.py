from flask import Flask, request, send_file, jsonify
from tts_engine import local_tts
import os, time, io, threading, logging

app = Flask(__name__)

TMP_DIR = "/tmp"
CHECKPOINT = 50
REST_TIME = 3
counter = 0
lock = threading.Lock()
log_stream = io.StringIO()

logging.basicConfig(stream=log_stream, level=logging.INFO)

@app.route("/api/voice", methods=["POST"])
def generate_voice():
    global counter
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Missing text"}), 400

    rate = float(data.get("rate", 1.25))
    pitch = float(data.get("pitch", 30.0))
    intonation = float(data.get("intonation", 0.6))
    emotion = data.get("emotion")

    try:
        buf = local_tts(text, rate=rate, pitch=pitch, intonation=intonation, emotion=emotion)
        logging.info(f"Generated voice for: {text[:10]}...")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    with lock:
        counter += 1
        if counter >= CHECKPOINT:
            _cleanup_logs_and_pause()

    return send_file(buf, mimetype="audio/wav")

def _cleanup_logs_and_pause():
    global counter
    try:
        log_stream.seek(0)
        log_stream.truncate(0)
        logging.info("Logs cleared.")
        for f in os.listdir(TMP_DIR):
            if f.startswith("voice_"):
                try:
                    os.remove(os.path.join(TMP_DIR, f))
                except OSError:
                    pass
    finally:
        counter = 0
        time.sleep(REST_TIME)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
