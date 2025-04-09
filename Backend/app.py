from flask import Flask, render_template, request, redirect, url_for
import os
import json
import hashlib
from verification import verification  # Assuming this is your OTP verification module

# File paths
USER_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")
DOMAINS_FILE = os.path.join(os.path.dirname(__file__), "data", "emails.json")

# Load user info
def load():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as file:
                data = file.read().strip()
                return json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {}
    return {}

# Load email domains
def load_domains():
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, "r") as file:
            data = json.load(file)
            return data.get("valid_domains", [])
    return {}

# Save user info
def save(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Password hashing function
def hashing(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize Flask app
app = Flask(__name__, template_folder='../Frontend', static_folder='../Frontend')

# Routes
@app.route('/')
def home():
    return render_template('index.html')  # Home page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load()
        if username in users and users[username]['password'] == hashing(password):
            return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            return "Invalid login credentials"
    
    return render_template('login.html')  # Login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        users = load()
        valid_domains = load_domains()

        # Check username availability
        if username in users:
            return "Username already taken."

        # Check email domain validity
        domain = email.split('@')[-1]
        if domain not in valid_domains:
            return "Invalid email domain."

        # Check if email already exists
        if any(user['email'] == email for user in users.values()):
            return "Email already taken."

        # Check password match
        if password != confirm_password:
            return "Passwords do not match."

        # Verify OTP
        otp = verification(email)  # Assuming this returns the OTP
        otp_input = request.form['otp']
        if otp_input != otp:
            return "Incorrect verification code."

        # Save user info
        users[username] = {"email": email, "password": hashing(password)}
        save(users)
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('register.html')  # Registration page

if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode