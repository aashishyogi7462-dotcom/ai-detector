import os
import requests
import cv2
from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load ML model
model, vectorizer = pickle.load(open("model/model.pkl", "rb"))

# Upload folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# API keys
API_USER = "616926002"
API_SECRET = "DWVrJBW9KxWiLSvfFxZFV43YefBgyP6e"


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":

        text = request.form.get("text")
        image = request.files.get("image")
        video = request.files.get("video")

        # ================= TEXT =================
        if text and text.strip() != "":
            X = vectorizer.transform([text])
            prediction = model.predict(X)

            if prediction[0] == 1:
                result = "AI Generated Text"
            else:
                result = "Human Written Text"

        # ================= IMAGE =================
        elif image and image.filename != "":
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(filepath)

            url = "https://api.sightengine.com/1.0/check.json"

            params = {
                'models': 'genai',
                'api_user': API_USER,
                'api_secret': API_SECRET
            }

            files = {'media': open(filepath, 'rb')}
            response = requests.post(url, files=files, data=params)
            result_data = response.json()

            try:
                ai_score = result_data['type']['ai_generated']

                if ai_score > 0.5:
                    result = "AI Generated Image"
                else:
                    result = "Real Image"
            except:
                result = "Error analyzing image"

        # ================= VIDEO =================
        elif video and video.filename != "":
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(filepath)

            cap = cv2.VideoCapture(filepath)
            success, frame = cap.read()

            if success:
                frame_path = os.path.join(app.config["UPLOAD_FOLDER"], "frame.jpg")
                cv2.imwrite(frame_path, frame)

                url = "https://api.sightengine.com/1.0/check.json"

                params = {
                    'models': 'genai',
                    'api_user': API_USER,
                    'api_secret': API_SECRET
                }

                files = {'media': open(frame_path, 'rb')}
                response = requests.post(url, files=files, data=params)
                result_data = response.json()

                try:
                    ai_score = result_data['type']['ai_generated']

                    if ai_score > 0.5:
                        result = "AI Generated Video"
                    else:
                        result = "Real Video"
                except:
                    result = "Error analyzing video"

            else:
                result = "Video processing error"

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)