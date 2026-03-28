from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def home():
    text_result = None
    image_result = None
    video_result = None

    if request.method == "POST":

        # TEXT
        text = request.form.get("text")
        if text and text.strip() != "":
            text_result = "🧠 Text Result: AI Generated"

        # IMAGE
        image = request.files.get("image")
        if image and image.filename != "":
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(image_path)
            image_result = "🖼️ Image Result: Fake Image"

        # VIDEO
        video = request.files.get("video")
        if video and video.filename != "":
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(video_path)
            video_result = "🎥 Video Result: Deepfake Detected"

    return render_template(
        "index.html",
        text_result=text_result,
        image_result=image_result,
        video_result=video_result
    )


if __name__ == "__main__":
    app.run(debug=True)