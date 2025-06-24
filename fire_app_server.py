from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

latest_detection = {
    "fire_level": None,
    "smoke_level": None,
    "image_path": None,
    "timestamp": None
}

@app.route("/")
def index():
    return render_template("index.html", data=latest_detection)

@app.route("/api/detection", methods=["POST"])
def receive_detection():
    global latest_detection
    fire_level = request.form.get("fire_level")
    smoke_level = request.form.get("smoke_level")
    file = request.files.get("image")

    if not all([fire_level, smoke_level, file]):
        return "Missing data", 400

    filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    latest_detection = {
        "fire_level": float(fire_level),
        "smoke_level": float(smoke_level),
        "image_path": filepath,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return jsonify({"status": "received"}), 200

@app.route("/api/user_response", methods=["POST"])
def user_response():
    user_choice = request.json.get("choice")
    print(f"🟢 User responded: {user_choice}")
    return jsonify({"status": "response recorded"}), 200

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
