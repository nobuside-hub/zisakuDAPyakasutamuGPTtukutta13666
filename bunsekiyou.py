from flask import Flask, request, jsonify
from bunsekiyou import DynamicCore

app = Flask(__name__)
core = DynamicCore()

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    user_input = data.get("input", "")
    result = core.request_handler(user_input)
    return jsonify({"result": result})

@app.route("/")
def home():
    return "DynamicCore AI System is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
