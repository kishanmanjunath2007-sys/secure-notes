 from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

# Simple in-memory storage (temporary)
notes_list = []

# 🔥 Home route (fix white page)
@app.route("/")
def home():
    return redirect("/login")

# 🔐 Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/notes")
    return render_template("login.html")

# 📝 Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/login")
    return render_template("register.html")

# 📒 Notes page
@app.route("/notes", methods=["GET", "POST"])
def notes():
    if request.method == "POST":
        note = request.form.get("note")
        if note:
            notes_list.append(note)
    return render_template("notes.html", notes=notes_list)

# 🚀 Run (Render compatible)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
