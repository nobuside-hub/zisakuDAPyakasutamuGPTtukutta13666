import os
import datetime
import random
import gc
from flask import Flask, request, jsonify

# ==============================
# DynamicCore クラス
# ==============================
class DynamicCore:
    def __init__(self):
        self.memory = {}
        self.active_module = None
        self.logs = []
        self.mode = "standard"

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(entry)

    def analyze_request(self, user_input):
        """ユーザー入力から目的を判定"""
        self.log(f"Request received: {user_input}")
        text = user_input.lower()
        if "構想" in text or "アイデア" in text:
            self.mode = "conceptual"
            return "concept_generation"
        elif "分析" in text or "解析" in text:
            return "text_analysis"
        elif "予測" in text or "未来" in text:
            return "forecast"
        elif "シミュレーション" in text or "模擬" in text:
            return "simulation"
        else:
            return "unknown"

    def spawn_module(self, spec):
        """動的モジュール生成"""
        self.log(f"Spawning module for spec: {spec}")

        def extract_keywords(text):
            return [w for w in text.split() if len(w) > 2]

        def detect_tone(text):
            return "positive" if "嬉" in text or "楽" in text else "neutral"

        def run_simulation(scenario):
            return f"Simulating: {scenario[:30]}..."

        def predict_trend(data):
            return {"trend": "上昇傾向", "confidence": 0.84}

        def generate_concept(prompt):
            ideas = [
                "融合的知性の設計",
                "自己再帰的創造のアルゴリズム",
                "共感を模倣する抽象構造",
                "思考の断片から生まれる秩序"
            ]
            random.shuffle(ideas)
            return {
                "base_prompt": prompt,
                "generated_concepts": ideas[:2],
                "mode": "conceptual"
            }

        if spec == "text_analysis":
            code = lambda x: {"keywords": extract_keywords(x), "tone": detect_tone(x)}
        elif spec == "simulation":
            code = lambda x: run_simulation(x)
        elif spec == "forecast":
            code = lambda x: predict_trend(x)
        elif spec == "concept_generation":
            code = lambda x: generate_concept(x)
        else:
            code = lambda x: "対応外の処理です"

        return type("TempModule", (), {"run": code})()

    def clear_logs(self, keep_errors=False):
        """ログ削除"""
        if keep_errors:
            self.logs = [l for l in self.logs if "[ERROR]" in l]
        else:
            self.logs.clear()
        gc.collect()

    def request_handler(self, user_input):
        """入力処理メイン"""
        spec = self.analyze_request(user_input)
        self.active_module = self.spawn_module(spec)
        try:
            result = self.active_module.run(user_input)
            if self.mode == "conceptual":
                self.log("Conceptual reasoning executed.")
            else:
                self.log("Task complete.")
        except Exception as e:
            self.log(f"Execution failed: {e}", level="ERROR")
            result = {"error": str(e)}
        finally:
            self.clear_logs(keep_errors=True)
        return result


# ==============================
# Flaskアプリ設定
# ==============================
app = Flask(__name__)
core = DynamicCore()

@app.route("/process", methods=["POST"])
def process():
    """ユーザー入力を処理"""
    data = request.get_json()
    if not data or "user_input" not in data:
        return jsonify({"error": "user_input が必要です"}), 400
    result = core.request_handler(data["user_input"])
    return jsonify(result)

@app.route("/")
def home():
    return "DynamicCore AI System is running."

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Renderが指定したPORTを使用
    app.run(host="0.0.0.0", port=port)
