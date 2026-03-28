from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 🔑 Sightengine API
API_USER = "616926002"
API_SECRET = "DWVrJBW9KxWiLSvfFxZFV43YefBgyP6e"


# -------- IMAGE --------
def analyze_image(path):
    url = "https://api.sightengine.com/1.0/check.json"

    files = {'media': open(path, 'rb')}
    data = {
        'models': 'genai,faces,deepfake',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    response = requests.post(url, files=files, data=data)

    try:
        result = response.json()
        return f"🖼 AI Score: {result.get('type', 'Analyzed')}"
    except:
        return "❌ Image analysis failed"


# -------- VIDEO --------
def analyze_video(path):
    url = "https://api.sightengine.com/1.0/video/check.json"

    files = {'media': open(path, 'rb')}
    data = {
        'models': 'deepfake',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    response = requests.post(url, files=files, data=data)

    try:
        result = response.json()
        return f"🎥 Video Checked (Deepfake analysis)"
    except:
        return "❌ Video analysis failed"


@app.route("/", methods=["GET", "POST"])
def home():
    image_result = None
    video_result = None

    if request.method == "POST":

        # IMAGE
        image = request.files.get("image")
        if image and image.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(path)
            image_result = analyze_image(path)

        # VIDEO
        video = request.files.get("video")
        if video and video.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(path)
            video_result = analyze_video(path)

    return render_template("index.html",
                           image_result=image_result,
                           video_result=video_result)


if __name__ == "__main__":
    app.run(debug=True)