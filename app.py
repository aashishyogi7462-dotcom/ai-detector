from flask import Flask, render_template, request
import os
import cv2
from transformers import pipeline
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 🔥 LOAD MODEL (ONLY ONCE)
image_detector = pipeline("image-classification", model="umm-maybe/AI-image-detector")


# -------- TEXT ANALYSIS --------
def analyze_text(text):
    text_lower = text.lower()

    # 🔹 AI style words
    ai_words = [
        "in conclusion", "moreover", "furthermore",
        "overall", "thus", "hence",
        "significantly", "it is important to note"
    ]

    ai_score = sum(1 for w in ai_words if w in text_lower)

    words = text_lower.split()

    if len(words) < 5:
        return "⚠️ Text too short"

    # 🔹 repetition check
    unique_ratio = len(set(words)) / len(words)

    # 🔹 sentence length
    sentences = text.split(".")
    long_sentences = sum(1 for s in sentences if len(s.split()) > 15)

    # 🔥 decision logic
    if ai_score >= 2 and long_sentences >= 1:
        return "🤖 AI Generated (pattern detected)"

    if unique_ratio < 0.45:
        return "⚠️ Possible Copy / Repetitive Text"

    if ai_score == 1:
        return "⚠️ Uncertain (mixed)"

    return "🧠 Human Written"
# -------- IMAGE (MODEL BASED) --------
def analyze_image_model(path):
    try:
        img = Image.open(path)
        result = image_detector(img)[0]

        label = result.get("label", "Unknown")
        score = result.get("score", 0)

        # थोड़ा stable output
        if score < 0.55:
            return {"label": "Uncertain", "score": score}

        return {"label": label, "score": score}

    except Exception as e:
        print("Image Error:", e)
        return {"label": "error", "score": 0}


# -------- SIMPLE IMAGE (FOR VIDEO) --------
def analyze_image_simple(path):
    try:
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = gray.mean()

        if variance < 45 or brightness < 50:
            return {"label": "AI"}
        else:
            return {"label": "Real"}

    except:
        return {"label": "error"}


# -------- EXTRACT FRAMES --------
def extract_frames(video_path, output_folder="static/frames"):
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % 25 == 0:
            frame_path = os.path.join(output_folder, f"frame_{count}.jpg")
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)

        if len(frames) >= 6:
            break

        count += 1

    cap.release()
    return frames


# -------- VIDEO --------
def analyze_video(path):
    try:
        frames = extract_frames(path)

        if not frames:
            return "🎥 Unable to analyze"

        ai_count = 0
        real_count = 0

        for frame in frames:
            res = analyze_image_simple(frame)

            if "AI" in res["label"]:
                ai_count += 1
            else:
                real_count += 1

        total = len(frames)

        if ai_count > real_count:
            return f"🤖 AI Video ({ai_count}/{total})"
        elif real_count > ai_count:
            return f"🧠 Real Video ({real_count}/{total})"
        else:
            return f"⚠️ Uncertain ({total})"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# -------- MAIN ROUTE --------
@app.route("/", methods=["GET", "POST"])
def home():
    text_result = None
    image_result = None
    video_result = None
    image_path = None
    video_path = None

    if request.method == "POST":

        # TEXT
        text = request.form.get("text")
        if text and text.strip():
            text_result = analyze_text(text)

        # IMAGE
        image = request.files.get("image")
        if image and image.filename != "":
            video_path = None

            path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(path)

            res = analyze_image_model(path)

            label = res.get("label", "Unknown")
            score = res.get("score", 0)

            if "AI" in label:
                image_result = f"🤖 {label} ({score*100:.0f}%)"
            elif "Real" in label:
                image_result = f"🧠 {label} ({score*100:.0f}%)"
            else:
                image_result = f"⚠️ {label} ({score*100:.0f}%)"

            image_path = path

        # VIDEO
        video = request.files.get("video")
        if video and video.filename != "":
            image_path = None

            path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(path)

            video_result = analyze_video(path)
            video_path = path

    return render_template("index.html",
                           text_result=text_result,
                           image_result=image_result,
                           video_result=video_result,
                           image_path=image_path,
                           video_path=video_path)


if __name__ == "__main__":
    app.run(debug=True)