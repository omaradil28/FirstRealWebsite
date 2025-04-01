from flask import Flask, render_template, request, redirect, url_for, flash
import json
import hashlib
import os
from verification import verification

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session and flash messages

USER_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")
DOMAINS_FILE = os.path.join(os.path.dirname(__file__), "data", "emails.json")

# Load user info
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            data = file.read().strip()
            return json.loads(data) if data else {}
    return {}

# Save user info
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Password hashing
def hashing(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load valid email domains
def load_domains():
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, "r") as file:
            data = json.load(file)
            return data.get("valid_domains", [])
    return []

# Registration page logic
@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    valid_domains = load_domains()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if username is taken
        if username in users:
            flash('Username already taken. Try another one.', 'danger')
            return redirect(url_for('register'))

        # Check if email domain is valid
        domain = email.split('@')[-1]
        if domain not in valid_domains:
            flash('Invalid email domain. Please enter a valid domain.', 'danger')
            return redirect(url_for('register'))

        # Check if email is already taken
        if any(info.get("email") == email for info in users.values()):
            flash('Email already taken. Try another one.', 'danger')
            return redirect(url_for('register'))

        # Check password match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # Send verification code to email
        otp = verification(email)

        # Get user verification code input
        verify_code = request.form['verify_code']

        if verify_code.strip() != otp:
            flash('Incorrect verification code.', 'danger')
            return redirect(url_for('register'))

        # Save the user if everything is valid
        users[username] = {
            "email": email,
            "password": hashing(password),
        }
        save_users(users)
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and hashing(password) == users[username]["password"]:
            flash(f'Login successful! Welcome back, {username}', 'success')
            return redirect(url_for('home'))  # Redirect to home or dashboard
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
