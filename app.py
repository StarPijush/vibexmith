from flask import Flask, render_template, request, redirect, url_for, session, abort
import json, os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"

DATA_FILE = "data/requests.json"
ADMIN_FILE = "data/admin.json"


# ---------- HELPERS ----------
def load_requests():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_requests(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_admin():
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_admin(data):
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def admin_required():
    return session.get("admin_logged_in")


# ---------- PUBLIC ----------
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
        abort(400)

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


# ---------- AUTH ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = load_admin()
        if (
            request.form["username"] == admin["username"]
            and check_password_hash(admin["password"], request.form["password"])
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- ADMIN ----------
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


# ---------- CHANGE PASSWORD ----------
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if not admin_required():
        return redirect(url_for("login"))

    error = success = None
    admin = load_admin()

    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if not check_password_hash(admin["password"], old):
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

@app.route("/mark-read/<int:index>")
def mark_read(index):
    with open("requests.json", "r") as f:
        data = json.load(f)

    if 0 <= index < len(data):
        data[index]["status"] = "read"

    with open("requests.json", "w") as f:
        json.dump(data, f, indent=4)

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)



