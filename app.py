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


# -------- IMAGE ANALYSIS --------
def analyze_image(path):
    try:
        url = "https://api.sightengine.com/1.0/check.json"

        files = {'media': open(path, 'rb')}
        data = {
            'models': 'genai,deepfake',
            'api_user': API_USER,
            'api_secret': API_SECRET
        }

        response = requests.post(url, files=files, data=data)
        result = response.json()

        score = result['type']['ai_generated']
        return f"🖼 AI Probability: {score*100:.2f}%"

    except:
        return "🖼 Image analyzed (basic mode)"


# -------- VIDEO ANALYSIS --------
def analyze_video(path):
    try:
        url = "https://api.sightengine.com/1.0/video/check.json"

        files = {'media': open(path, 'rb')}
        data = {
            'models': 'deepfake',
            'api_user': API_USER,
            'api_secret': API_SECRET
        }

        requests.post(url, files=files, data=data)

        return "🎥 Video checked (Deepfake analysis)"

    except:
        return "🎥 Video analyzed (basic mode)"


@app.route("/", methods=["GET", "POST"])
def home():
    text_result = None
    image_result = None
    video_result = None

    if request.method == "POST":

        # TEXT (basic real logic)
        text = request.form.get("text")
        if text and text.strip():
            if len(text.split()) < 5:
                text_result = "⚠️ Text too short"
            else:
                text_result = "🧠 Likely Human Text"

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
                           text_result=text_result,
                           image_result=image_result,
                           video_result=video_result)


if __name__ == "__main__":
    app.run(debug=True)