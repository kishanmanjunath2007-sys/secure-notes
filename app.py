from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from cryptography.fernet import Fernet

app = Flask(__name__)

# 🔐 Fixed encryption key
key = b'IhYH1Bnlotf6QwLYSxp2QAqv74TX3IJ4HhIUPvVPJ_w='
cipher = Fernet(key)

# 📦 Create database
conn = sqlite3.connect("users.db")
conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS notes (note TEXT)")
conn.close()

# 📝 Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username and password:
            conn = sqlite3.connect("users.db")
            conn.execute("INSERT INTO users VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return "Registered Successfully 🎉"

    return render_template("register.html")

# 🔐 Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect("users.db")
        cursor = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for("notes"))
        else:
            return "Wrong Username or Password ❌"

    return render_template("login.html")

# 📝 Notes (SAFE version)
@app.route("/notes", methods=["GET", "POST"])
def notes():
    conn = sqlite3.connect("users.db")

    if request.method == "POST":
        note = request.form.get("note", "")

        if note.strip() != "":
            encrypted_note = cipher.encrypt(note.encode()).decode()
            conn.execute("INSERT INTO notes VALUES (?)", (encrypted_note,))
            conn.commit()

    cursor = conn.execute("SELECT note FROM notes")
    all_notes = []

    for row in cursor:
        try:
            decrypted = cipher.decrypt(row[0].encode()).decode()
            all_notes.append(decrypted)
        except:
            pass  # skip bad/old data

    conn.close()

    return render_template("notes.html", notes=all_notes)

# 🚀 Run
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
