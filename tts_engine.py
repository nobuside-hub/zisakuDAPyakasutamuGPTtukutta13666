import subprocess, os

EMOTION_PRESETS = {
    "happy":    {"rate": 1.4, "pitch": 40, "intonation": 0.8},
    "angry":    {"rate": 1.3, "pitch": 35, "intonation": 0.9},
    "sad":      {"rate": 0.9, "pitch": 25, "intonation": 0.4},
    "bashful":  {"rate": 1.1, "pitch": 45, "intonation": 0.5},
}

def local_tts(text, output_path, rate=1.25, pitch=30.0, intonation=0.6, emotion=None):
    """OpenJTalkでTTS生成（動的パラメータ＋感情対応）"""

    if emotion in EMOTION_PRESETS:
        preset = EMOTION_PRESETS[emotion]
        rate, pitch, intonation = preset["rate"], preset["pitch"], preset["intonation"]

    dic_candidates = [
        "/var/lib/mecab/dic/open-jtalk/naist-jdic",
        "/usr/share/mecab/dic/open-jtalk/naist-jdic",
        "/usr/local/share/mecab/dic/open-jtalk/naist-jdic"
    ]
    voice_candidates = [
        "/usr/share/hts-voice/mei/mei_normal.htsvoice",
        "/usr/share/hts-voice/mei/mei_angry.htsvoice",
        "/usr/share/hts-voice/mei/mei_bashful.htsvoice"
    ]

    dic = next((d for d in dic_candidates if os.path.exists(d)), None)
    voice = next((v for v in voice_candidates if os.path.exists(v)), None)

    if not dic:
        raise FileNotFoundError("辞書パスが見つかりません。")
    if not voice:
        raise FileNotFoundError("音声モデルが見つかりません。")

    subprocess.run([
        "open_jtalk",
        "-x", dic,
        "-m", voice,
        "-r", str(rate),
        "-fm", str(pitch),
        "-a", str(intonation),
        "-ow", output_path
    ], input=text.encode("utf-8"), check=True)
