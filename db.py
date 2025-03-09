import pymongo
from flask import request

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
userdb = client['users']
users = userdb.customers

def insert_data():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        role = request.form.get('role', 'user')  # Default role is 'user' if not provided

        reg_user = {
            "name": name,
            "email": email,
            "password": password,
            "role": role  # Adding role field
        }

        if users.find_one({"email": email}) is None:
            users.insert_one(reg_user)
            return True
        else:
            return False

def check_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        user = {
            "email": email,
            "password": password
        }

        user_data = users.find_one(user)
        if user_data is None:
            return False, "", ""
        else:
            return True, user_data["name"], user_data.get("role", "user")  # Returning role
