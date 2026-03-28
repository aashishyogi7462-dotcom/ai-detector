import os
import requests
import cv2
from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load model
model, vectorizer = pickle.load(open("model/model.pkl", "rb"))

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# API KEYS (apni dalna)
API_USER = "YOUR_API_USER"
API_SECRET = "YOUR_API_SECRET"


@app.route("/", methods=["GET", "POST"])
def home():
    text_result = None
    image_result = None
    video_result = None

    if request.method == "POST":

        text = request.form.get("text")
        image = request.files.get("image")
        video = request.files.get("video")

        # ===== TEXT =====
        if text and text.strip() != "":
            X = vectorizer.transform([text])
            prediction = model.predict(X)
            text_result = "AI Generated Text 🤖" if prediction[0] == 1 else "Human Written Text 🧑"

        # ===== IMAGE =====
        if image and image.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(path)

            try:
                response = requests.post(
                    "https://api.sightengine.com/1.0/check.json",
                    files={'media': open(path, 'rb')},
                    data={
                        'models': 'genai',
                        'api_user': API_USER,
                        'api_secret': API_SECRET
                    }
                ).json()

                score = response['type']['ai_generated']
                image_result = "AI Generated Image 🤖" if score > 0.5 else "Real Image 📷"

            except:
                image_result = "Error analyzing image ❌"

        # ===== VIDEO =====
        if video and video.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(path)

            cap = cv2.VideoCapture(path)
            success, frame = cap.read()

            if success:
                frame_path = os.path.join(app.config["UPLOAD_FOLDER"], "frame.jpg")
                cv2.imwrite(frame_path, frame)

                try:
                    response = requests.post(
                        "https://api.sightengine.com/1.0/check.json",
                        files={'media': open(frame_path, 'rb')},
                        data={
                            'models': 'genai',
                            'api_user': API_USER,
                            'api_secret': API_SECRET
                        }
                    ).json()

                    score = response['type']['ai_generated']
                    video_result = "AI Generated Video 🎥🤖" if score > 0.5 else "Real Video 🎥"

                except:
                    video_result = "Error analyzing video ❌"
            else:
                video_result = "Video processing error ❌"

    return render_template("index.html",
                           text_result=text_result,
                           image_result=image_result,
                           video_result=video_result)


if __name__ == "__main__":
    app.run(debug=True)