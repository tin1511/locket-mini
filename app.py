from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DB
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS likes(
    id INTEGER PRIMARY KEY,
    post_id INTEGER
    )
   """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS comments(
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    username TEXT,
    content TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/like/<int:post_id>")
def like(post_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("INSERT INTO likes(post_id) VALUES(?)", (post_id,))
    conn.commit()
    conn.close()

    return redirect("/home")

@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    content = request.form["content"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("INSERT INTO comments(post_id,username,content) VALUES(?,?,?)",
              (post_id, session["user"], content))

    conn.commit()
    conn.close()

    return redirect("/home")

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        sqlite3.connect("/tmp/users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/home")

    return render_template("login.html")

# HOME
@app.route("/home")
def home():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()

    c.execute("SELECT * FROM comments")
    comments = c.fetchall()

    conn.close()

    return render_template("home.html", posts=posts, comments=comments, user=session["user"])

# UPLOAD POST
@app.route("/post", methods=["POST"])
def post():
    if "user" not in session:
        return "no"

    file = request.files["photo"]
    caption = request.form["caption"]

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO posts(username,image,caption) VALUES(?,?,?)",
              (session["user"], path, caption))
    conn.commit()
    conn.close()

    return redirect("/home")

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT username,image FROM posts WHERE id=?", (id,))
    post = c.fetchone()

    if post and post[0] == session["user"]:
        if os.path.exists(post[1]):
            os.remove(post[1])

        c.execute("DELETE FROM posts WHERE id=?", (id,))
        conn.commit()

    conn.close()
    return redirect("/home")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
