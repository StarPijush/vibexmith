from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
import json, os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ================================
# Flask App Setup
# ================================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET")  # Use env in production

DATA_FILE = os.path.join("data", "requests.json")
ADMIN_FILE = os.path.join("data", "admin.json")


# ================================
# Helper Functions
# ================================
def load_json(file_path, default=None):
    """Generic JSON loader"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(file_path, data):
    """Generic JSON saver"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_requests():
    return load_json(DATA_FILE, default=[])


def save_requests(data):
    save_json(DATA_FILE, data)


def load_admin():
    return load_json(ADMIN_FILE)


def save_admin(data):
    save_json(ADMIN_FILE, data)


def admin_required():
    """Check if admin is logged in"""
    return session.get("admin_logged_in")


# ================================
# Public Routes
# ================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_request():
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not phone or not message:
        abort(400, description="Missing required fields")

    # Save request
    data = load_requests()
    data.append({
        "name": name,
        "phone": phone,
        "email": email,
        "message": message,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_requests(data)

    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


# ================================
# Authentication
# ================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = load_admin()
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if admin and username == admin.get("username") and check_password_hash(admin.get("password", ""), password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================================
# Admin Routes
# ================================
@app.route("/admin")
def admin():
    if not admin_required():
        return redirect(url_for("login"))

    return render_template("admin.html", requests=load_requests())


@app.route("/delete/<int:index>")
def delete(index):
    if not admin_required():
        return redirect(url_for("login"))

    data = load_requests()
    if index < 0 or index >= len(data):
        abort(404)

    data.pop(index)
    save_requests(data)
    return redirect(url_for("admin"))


# ================================
# Change Password
# ================================
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not admin_required():
        return redirect(url_for("login"))

    error = success = None
    admin = load_admin()

    if request.method == "POST":
        old = request.form.get("old_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not check_password_hash(admin.get("password", ""), old):
            error = "Current password is incorrect"
        elif new != confirm:
            error = "Passwords do not match"
        elif len(new) < 6:
            error = "Password too short"
        else:
            admin["password"] = generate_password_hash(new)
            save_admin(admin)
            success = "Password updated successfully"

    return render_template("change_password.html", error=error, success=success)


# ================================
# Run App
# ================================
if __name__ == "__main__":
    app.run(debug=True)
