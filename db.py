import os

import bcrypt
import pymongo
from argon2 import PasswordHasher
from flask import request
import re
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
userdb = client['brainTumor']
users = userdb.users
# Initialize PasswordHasher from argon2-cffi
ph = PasswordHasher()


def create_default_admin():
    """Create a default admin user if none exists."""
    admin_email = os.getenv("ADMIN_EMAIL", "braintumorpanel@gmail.com")  # Fallback for dev
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")     # Fallback for dev

    if users.find_one({"email": admin_email, "role": "admin"}) is None:
        hashed_password = ph.hash(admin_password)
        users.insert_one({
            "name": "Admin",
            "email": admin_email,
            "password": hashed_password,
            "role": "admin"
        })
        print(f"Default admin created: {admin_email} / {admin_password}")
    else:
        print("Default admin already exists.")


create_default_admin()
def insert_data():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        role = request.form.get('role', 'user')


        # Hash the password
        hashed_password = ph.hash(password)
        reg_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role ,

        }
        if role == 'doctor':
            reg_user['isVerified'] = False

        if users.find_one({"email": email}) is None:
            users.insert_one(reg_user)
            return True
        else:
            return False


def check_user(email, password):  # Now accepts email and password as parameters
    # Find the user in the database by email
    user = {
        "email": email,
    }

    user_data = users.find_one(user)

    if user_data:
        try:
            # Verify the password
            if ph.verify(user_data['password'], password):
                user_type = user_data.get("role", "user")  # Default to 'user' if role is missing
                return True, user_data["name"], user_type
            else:
                print("Password verification failed.")
                return False, "", ""  # Return failure if password verification fails
        except Exception as e:
            print(f"Password verification error: {e}")
            return False, "", ""  # Return failure in case of any error
    else:
        print("User not found.")
        return False, "", ""  # Return failure if no user is found
