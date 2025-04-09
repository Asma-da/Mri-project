import numpy as np
import cv2
from keras_preprocessing.image import ImageDataGenerator

import db
from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file, session
from preprocess import preprocess_image  # Import the preprocessing function
from io import BytesIO
from argon2 import PasswordHasher
from bson.objectid import ObjectId

app = Flask(__name__)

ph = PasswordHasher()

app.secret_key = "sEYTK%KF5urhba%m15engfrif"

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':

        if request.content_type and "application/json" not in request.content_type:
            return jsonify({"error": "Invalid content type. Please send JSON data."}), 415

        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400

            email = data.get('email')
            password = data.get('pass')

            if not email or not password:
                return jsonify({"error": "Email and password are required"}), 400

            result = db.check_user(email, password)
            if result is None:
                return jsonify({"error": "User not found"}), 404

            status, username, user_type = result

            if status:
                # Save session info
                session['email'] = email
                session['user_type'] = user_type


                if user_type == 'admin':
                    redirect_url = url_for('admin_dashboard')
                elif user_type == 'doctor':
                    redirect_url = url_for('doctor_dashboard')
                else:
                    redirect_url = url_for('user_dashboard')

                return jsonify({
                    "username": username,
                    "status": status,
                    "user_type": user_type,
                    "redirect_url": redirect_url
                })

            return jsonify({"error": "Incorrect password"}), 401

        except Exception as e:
            print(f" Debug: Exception occurred: {str(e)}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    # Already logged in , so the user will be directed based on the role
    if 'email' in session and 'user_type' in session:
        user_type = session['user_type']
        if user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user_type == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    try:
        data = request.get_json()
        if db.users.find_one({"email": data['email']}):
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        hashed_password = ph.hash(data['pass'])

        user_data = {
            "name": data['name'],
            "email": data['email'],
            "password": hashed_password,
            "role": data['role']
        }

        if data['role'] == 'doctor':
            user_data['isVerified'] = False

        db.users.insert_one(user_data)

        return jsonify({
            'success': True,
            'message': 'Doctor account pending approval' if data['role'] == 'doctor' else 'Registration successful'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    return render_template("singup.html")

@app.route('/doctor_dashboard', methods=['GET'])
def doctor_dashboard():
    email = session.get('email')

    if not email:
        return redirect(url_for('signin'))

    user = db.users.find_one({'email': email})

    if not user:
        return "User not found", 404

    if not user.get('isVerified', False):
        return render_template('doctor/waiting_approval.html', user=user)

    return render_template('doctor/dashboard.html', user=user)




@app.route('/admin_dashboard')
def admin_dashboard():
    users = list(db.users.find())

    pending_doctors = db.users.count_documents({"role": "doctor", "isVerified": False})
    approved_doctors = db.users.count_documents({"role": "doctor", "isVerified": True})
    total_users = db.users.count_documents({})
    regular_users = db.users.count_documents({"role": "user"})

    stats = {
        "total_users": total_users,
        "pending_doctors": pending_doctors,
        "regular_users": regular_users,
        "approved_doctors": approved_doctors
    }
    print(pending_doctors)
    return render_template("admin.html", users=users, stats=stats)


@app.route('/approve_doctor/<user_id>', methods=['POST'])
def approve_doctor(user_id):
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"isVerified": True}})
    return jsonify({"status": "success"})


@app.route('/reject_doctor/<user_id>', methods=['POST'])
def reject_doctor(user_id):
    db.users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"status": "success"})

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    db.users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"status": "success"})

image_datagen = ImageDataGenerator(rescale=1./255)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

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
    # Preprocess the image (rescale to [0, 1] using ImageDataGenerator)
    image = cv2.resize(image, (224, 224))  # Resize the image to match model input size (224x224)
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    preprocessed_image = image_datagen.flow(image)  # Apply the rescaling transformation

    # Get the transformed image (first batch)
    preprocessed_image = preprocessed_image[0]

    # Convert the preprocessed image to the correct format for sending it as a response
    preprocessed_image = (preprocessed_image * 255).astype(np.uint8)  # Convert to 8-bit format
    _, buffer = cv2.imencode('.jpg', preprocessed_image)

    # Return the processed image as a response
    return send_file(BytesIO(buffer), mimetype='image/jpeg')


@app.route('/blog')
def blog():
    return render_template("blog.html")


@app.route('/user_dashboard')
def user_dashboard():
    return render_template("user.html")


@app.route('/contact_us')
def contact_us():
    return render_template("contact.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
