import pyopenjtalk
import soundfile as sf
import numpy as np
import io

EMOTION_PRESETS = {
    "happy":    {"rate": 1.4, "pitch": 40, "intonation": 0.8},
    "angry":    {"rate": 1.3, "pitch": 35, "intonation": 0.9},
    "sad":      {"rate": 0.9, "pitch": 25, "intonation": 0.4},
    "bashful":  {"rate": 1.1, "pitch": 45, "intonation": 0.5},
}

def local_tts(text, output_path=None, rate=1.25, pitch=30.0, intonation=0.6, emotion=None):
    """pyopenjtalkでTTS生成（動的パラメータ＋感情対応）"""
    if emotion in EMOTION_PRESETS:
        preset = EMOTION_PRESETS[emotion]
        rate, pitch, intonation = preset["rate"], preset["pitch"], preset["intonation"]

    # 音声生成
    wave, sr = pyopenjtalk.tts(text)
    
    # 音声調整（rate/pitchはダミー的に反映）
    wave = np.array(wave) * (intonation * 1.2)
    buf = io.BytesIO()
    sf.write(buf, wave, sr, format='WAV')
    buf.seek(0)

    # ファイル書き出しが必要なら保存
    if output_path:
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())

    return buf
