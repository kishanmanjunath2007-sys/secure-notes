from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# 🔐 Encryption key
key = b'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE='
cipher = Fernet(key)

# ---------------- USER DB ----------------
def init_user_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.commit()
    conn.close()

init_user_db()

# ---------------- NOTES DB ----------------
def init_notes_db():
    conn = sqlite3.connect("notes.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            note BLOB
        )
    """)
    conn.commit()
    conn.close()

init_notes_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return redirect("/login")

# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user"] = username
            return redirect("/notes")
        else:
            return "Invalid login"

    return render_template("login.html")

# -------- NOTES --------
@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("notes.db")
    cur = conn.cursor()

    # SAVE NOTE
    if request.method == "POST":
        note = request.form.get("note")
        if note:
            encrypted_note = cipher.encrypt(note.encode())
            cur.execute("INSERT INTO notes (username, note) VALUES (?, ?)",
                        (session["user"], encrypted_note))
            conn.commit()

    # FETCH NOTES
    cur.execute("SELECT id, note FROM notes WHERE username=?", (session["user"],))
    data = cur.fetchall()
    conn.close()

    # DECRYPT
    notes = []
    for n in data:
        decrypted = cipher.decrypt(n[1]).decode()
        notes.append((n[0], decrypted))

    return render_template("notes.html", notes=notes)

# -------- DELETE --------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("notes.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=? AND username=?", (id, session["user"]))
    conn.commit()
    conn.close()

    return redirect("/notes")

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
