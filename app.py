from flask import Flask, request, send_file, jsonify, after_this_request
from tts_engine import local_tts
import os, time, threading, io, logging

app = Flask(__name__)

# ---- 設定 ----
TMP_DIR = "/tmp"
CHECKPOINT = 50  # 50件ごとに掃除＋休息
REST_TIME = 3    # 秒
counter = 0
log_stream = io.StringIO()

logging.basicConfig(stream=log_stream, level=logging.INFO)

@app.route("/api/voice", methods=["POST"])
def generate_voice():
    global counter
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Missing text"}), 400

    # 動的パラメータ（デフォルト値あり）
    rate = float(data.get("rate", 1.25))
    pitch = float(data.get("pitch", 30.0))
    intonation = float(data.get("intonation", 0.6))
    emotion = data.get("emotion")  # プリセット対応

    filename = os.path.join(TMP_DIR, f"voice_{int(time.time())}.wav")

    try:
        local_tts(text, filename, rate=rate, pitch=pitch, intonation=intonation, emotion=emotion)
        logging.info(f"Generated {filename}")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 音声送信後に削除
    @after_this_request
    def cleanup(response):
        try:
            os.remove(filename)
            logging.info(f"Deleted {filename}")
        except OSError:
            pass
        return response

    # 定期チェックポイント
    counter += 1
    if counter >= CHECKPOINT:
        _cleanup_logs_and_pause()

    return send_file(filename, mimetype="audio/wav")


def _cleanup_logs_and_pause():
    """ログ・一時ファイルを削除して小休止"""
    global counter
    try:
        # ログ掃除
        log_stream.seek(0)
        log_stream.truncate(0)
        logging.info("Logs cleared.")

        # 古い/tmpファイルを削除
        for f in os.listdir(TMP_DIR):
            if f.startswith("voice_"):
                try:
                    os.remove(os.path.join(TMP_DIR, f))
                except OSError:
                    pass
        logging.info("Temp files cleared.")
    finally:
        counter = 0
        time.sleep(REST_TIME)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
