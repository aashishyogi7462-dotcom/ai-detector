import os
import requests
import cv2
from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load model
model, vectorizer = pickle.load(open("model/model.pkl", "rb"))

# Upload folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ================= API KEYS =================
API_USER = "616926002"
API_SECRET = "DWVrJBW9KxWiLSvfFxZFV43YefBgyP6e"
# ===========================================


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    status = None

    if request.method == "POST":

        text = request.form.get("text")
        image = request.files.get("image")
        video = request.files.get("video")

        # ================= TEXT =================
        if text and text.strip() != "":
            X = vectorizer.transform([text])
            prediction = model.predict(X)

            if prediction[0] == 1:
                ai_result = "AI Generated"
            else:
                ai_result = "Human Written"

            fake_keywords = ["breaking", "shocking", "viral", "alert", "exclusive"]

            if any(word in text.lower() for word in fake_keywords):
                news_result = "Fake News"
            else:
                news_result = "Real News"

            status = "Successfully Analyzed"
            result = f"{ai_result} + {news_result}"

        # ================= IMAGE =================
        elif image and image.filename != "":
            if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                result = "Please upload valid image (jpg/png)"
                status = None
            else:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
                image.save(filepath)

                status = "Successfully Analyzed"

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
            if not video.filename.lower().endswith(('.mp4', '.avi', '.mov')):
                result = "Please upload valid video"
                status = None
            else:
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
                video.save(filepath)

                status = "Successfully Analyzed"

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
                    result = "Could not read video"

        else:
            result = None
            status = None

    return render_template("index.html", result=result, status=status)


if __name__ == "__main__":
    app.run(debug=True)
    @app.route("/", methods=["GET", "POST"])
    def home():
       return render_template("index.html")