from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

photos = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["photo"]

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(path)

    url = "/" + path
    photos.insert(0, url)

    return jsonify({"url": url})

@app.route("/photos")
def get_photos():
    return jsonify(photos)

# 🔥 FIX RENDER PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
