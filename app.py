
import numpy as np
import cv2

import db
import json
from flask import Flask, request, render_template, json, redirect, url_for, jsonify,send_file
from preprocess import preprocess_image  # Import the preprocessing function
from io import BytesIO


app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    return render_template("signup.html")



@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # If it's a POST request, check the user
        result = db.check_user()
        print(result)

        # Check if result is None or not
        if result is None:
            return json.dumps({"error": "User not found"})

        status, username, user_type = result

        data = {
            "username": username,
            "status": status,
            "user_type": user_type
        }

        if status:
            return json.dumps(data)
        else:
            return json.dumps(data)

        # If it's a GET request (when just visiting the page)
    return render_template('signin.html')  # This will render the signin page without checking for a user
# Define the routes for the respective dashboards
@app.route('/doctor_dashboard')
def doctor_dashboard():
    return render_template("doc.html")

@app.route('/admin_dashboard')
def user_dashboard():
    return render_template("user.html")


@app.route('/register', methods = ['GET', 'POST'])
def register():
    status = db.insert_data()
    return json.dumps(status)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handles the image upload via POST method.
    Reads the image file, preprocesses it, and returns the preprocessed image.
    """
    if request.method == 'GET':
        return render_template('upload.html')  # Render the file upload form

    if 'file' not in request.files:
        print("No file part in request")
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return "No selected file", 400

    # Read the image file into memory
    file_stream = file.read()
    if not file_stream:
        print("File stream is empty")
        return "Empty file", 400

    # Convert the file stream into a NumPy array (image buffer)
    npimg = np.frombuffer(file_stream, np.uint8)
    print(f"npimg size: {npimg.size}")  # Debugging size of the image buffer

    # Decode the image
    image = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)  # Decode the image as grayscale
    if image is None:
        print("Failed to decode image")
        return "Invalid image format", 400

    print(f"Decoded image shape: {image.shape}")  # Debugging image shape

    # Preprocess the image
    preprocessed_image = preprocess_image(image)

    # Convert the preprocessed image to the correct format for sending it as a response
    preprocessed_image = (preprocessed_image * 255).astype(np.uint8)  # Convert to 8-bit format
    _, buffer = cv2.imencode('.jpg', preprocessed_image)  # Encode as JPEG

    # Return the processed image as a response
    return send_file(BytesIO(buffer), mimetype='image/jpeg')
if __name__ == '__main__':
    app.run(debug = True)