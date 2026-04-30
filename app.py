from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

notes_list = []

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            return redirect("/notes")
        return render_template("login.html")
    except Exception as e:
        return f"Login Error: {e}"

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            return redirect("/login")
        return render_template("register.html")
    except Exception as e:
        return f"Register Error: {e}"

@app.route("/notes", methods=["GET", "POST"])
def notes():
    try:
        if request.method == "POST":
            note = request.form.get("note")
            if note:
                notes_list.append(note)
        return render_template("notes.html", notes=notes_list)
    except Exception as e:
        return f"Notes Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
