def generate_yurika_voice(text):
    import requests, json, time
    res = requests.post(
        "http://localhost:50021/audio_query",  # ← http !!
        params={"text": text, "speaker": 25}
    )
    query = res.json()
    audio = requests.post(
        "http://localhost:50021/synthesis",     # ← http !!
        headers={"Content-Type": "application/json"},
        data=json.dumps(query),
        params={"speaker": 25}
    )
    filename = f"yurika_{int(time.time())}.wav"
    with open(filename, "wb") as f:
        f.write(audio.content)
    return filename
