from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------ USER DATABASE ------------------
def init_user_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.commit()
    conn.close()

init_user_db()

# ------------------ NOTES DATABASE ------------------
def init_notes_db():
    conn = sqlite3.connect("notes.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS notes (username TEXT, note TEXT)")
    conn.commit()
    conn.close()

init_notes_db()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return redirect("/login")

# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?)", (username, password))
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
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
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

    # Save note
    if request.method == "POST":
        note = request.form.get("note")
        if note:
            cur.execute("INSERT INTO notes VALUES (?, ?)", (session["user"], note))
            conn.commit()

    # Fetch notes
    cur.execute("SELECT note FROM notes WHERE username=?", (session["user"],))
    data = cur.fetchall()
    conn.close()

    notes = [n[0] for n in data]

    return render_template("notes.html", notes=notes)

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
