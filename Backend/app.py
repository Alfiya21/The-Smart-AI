from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_dance.contrib.google import make_google_blueprint, google
import sqlite3
import os
import json
from recommender import load_tools, get_matching_tools



app = Flask(__name__)
app.secret_key = 'supersecret'
bcrypt = Bcrypt(app)

# Google OAuth
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
google_bp = make_google_blueprint(redirect_to="google_login")
app.register_blueprint(google_bp, url_prefix="/login")

# Create DB if not exists
if not os.path.exists("database.db"):
    import models
    models.init_db()

from recommender import get_matching_tools

@app.route("/", methods=["GET", "POST"])
def home():
    tools = []
    query = ""
    selected_pricing = "all"
    selected_sort = "rating"
    selected_tag = ""
    selected_category = request.args.get("category", "")

    all_tools = load_tools()
    all_tags = sorted({tag for t in all_tools for tag in t.get("tags", [])})

    # User is trying to search (POST), but not logged in
    if request.method == "POST":
        if "user_id" not in session:
            flash("Please log in to search for tools.")
            return redirect(url_for("login"))

        # Proceed with search logic
        query = request.form.get("prompt", "").strip()
        selected_pricing = request.form.get("pricing", "all")
        selected_sort = request.form.get("rating", "desc")
        selected_tag = request.form.get("tag", "")

        tools = get_matching_tools(query)

        if selected_pricing != "all":
            tools = [t for t in tools if t.get("pricing", "").lower() == selected_pricing.lower()]
        if selected_tag:
            tools = [t for t in tools if selected_tag.lower() in [tag.lower() for tag in t.get("tags", [])]]
        if selected_sort == "asc":
            tools = sorted(tools, key=lambda x: x.get("rating", 0))
        else:
            tools = sorted(tools, key=lambda x: -x.get("rating", 0))

    return render_template(
        "index.html",
        tools=tools,
        tags=all_tags,
        selected_tag=selected_tag,
        selected_pricing=selected_pricing,
        selected_sort=selected_sort,
        query=query,
        categories=[
            "Video Editing",
            "Graphic design",
            "Programming",
            "Research & Assistant",
            "Audio & Music",
            "Content Writing",
            "Image Generation",
        ],
        category=selected_category
    )

@app.route('/category/<name>', methods=["GET", "POST"])
def category(name):
        
    
    all_tools = load_tools()
    query = ""
    tools = [tool for tool in all_tools if tool.get("category", "").lower() == name.lower()]
    all_tags = sorted({tag for t in all_tools for tag in t.get("tags", [])})

    selected_pricing = "all"
    selected_sort = "rating"
    selected_tag = ""

    if request.method == "POST":
        query = request.form.get("prompt", "").strip()
        selected_pricing = request.form.get("pricing", "all")
        selected_sort = request.form.get("rating", "rating")
        selected_tag = request.form.get("tag", "")

        tools = get_matching_tools(query) if query else tools

        if selected_pricing != "all":
            tools = [t for t in tools if t.get("pricing", "").lower() == selected_pricing.lower()]
        if selected_tag:
            tools = [t for t in tools if selected_tag.lower() in [tag.lower() for tag in t.get("tags", [])]]

        if selected_sort == "asc":
            tools = sorted(tools, key=lambda x: x.get("rating", 0))
        elif selected_sort == "desc":
            tools = sorted(tools, key=lambda x: -x.get("rating", 0))

    return render_template(
        "index.html",
        tools=tools,
        query=query,
        selected_tag=selected_tag,
        selected_pricing=selected_pricing,
        selected_sort=selected_sort,
        tags=all_tags,
        categories=[
            "Video Editing",
            "Graphic design",
            "Programming",
            "Research & Assistant",
            "Audio & Music",
            "Content Writing",
            "Image Generation"
        ],
        category=name
    )



@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Google login failed.")
        return redirect(url_for("login"))

    user_info = resp.json()
    username = user_info["email"]

    with sqlite3.connect("database.db") as conn:
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, "", "user"))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

    session["user_id"] = user[0]
    session["username"] = user[1]
    flash("✅ Logged in with Google")
    return redirect(url_for("home"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        with sqlite3.connect("database.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user:
            if bcrypt.check_password_hash(user[2], password):
                session["user_id"] = user[0]
                session["username"] = user[1]
                flash("✅ Logged in successfully!")
                return redirect(url_for("home"))
            else:
                flash("❌ Incorrect password.")
        else:
            flash("❌ Username not found.")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            with sqlite3.connect("users.db") as conn:
                conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, "user"))
                conn.commit()
            flash("✅ Registration successful")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("❌ Username already exists")
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]
        with sqlite3.connect("database.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user:
                hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
                conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))
                conn.commit()
                flash("Password reset successfully. You can now log in.")
                return redirect(url_for("login"))
            else:
                flash("Username not found.")
    return render_template("forgot_password.html")

@app.route('/change-password', methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("Login required.")
        return redirect(url_for("login"))

    if request.method == "POST":
        current_pw = request.form["current_password"]
        new_pw = request.form["new_password"]

        with sqlite3.connect("database.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
            if user and bcrypt.check_password_hash(user[2], current_pw):
                new_hashed = bcrypt.generate_password_hash(new_pw).decode("utf-8")
                conn.execute("UPDATE users SET password=? WHERE id=?", (new_hashed, session["user_id"]))
                conn.commit()
                flash("Password updated successfully.")
                return redirect(url_for("home"))
            else:
                flash("Current password is incorrect.")
    return render_template("change_password.html")

@app.route('/tools', methods=["GET", "POST"])
def tools():
    tools = []
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "")
        from recommender import get_matching_tools
        tools = get_matching_tools(query)
    else:
        with sqlite3.connect("database.db") as conn:
            tools = conn.execute("SELECT * FROM tools").fetchall()
    return render_template("tools.html", tools=tools, user=session.get("username"), query=query)

@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    with sqlite3.connect("database.db") as conn:
        tool = conn.execute("SELECT * FROM tools WHERE id=?", (tool_id,)).fetchone()
        reviews = conn.execute("SELECT comment FROM reviews WHERE tool_id=?", (tool_id,)).fetchall()
    return render_template("tool_detail.html", tool=tool, reviews=reviews)

@app.route('/add-tool', methods=["GET", "POST"])
def add_tool():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        data = (
            request.form["name"],
            request.form["category"],
            float(request.form["rating"]),
            request.form["url"],
            request.form["pricing"],
            request.form["tags"],
            request.form["description"],
            session["user_id"]
        )
        with sqlite3.connect("database.db") as conn:
            conn.execute('''
                INSERT INTO tools (name, category, rating, url, pricing, tags, description, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
            conn.commit()
        flash("Tool added successfully!")
        return redirect(url_for("tools"))
    return render_template("add_tool.html")

@app.route('/favorite/<int:tool_id>')
def favorite(tool_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    with sqlite3.connect("database.db") as conn:
        conn.execute("INSERT OR IGNORE INTO favorites (user_id, tool_id) VALUES (?, ?)", (session["user_id"], tool_id))
        conn.commit()
    flash("Added to favorites!")
    return redirect(url_for("tool_detail", tool_id=tool_id))

@app.route('/review/<int:tool_id>', methods=["POST"])
def review(tool_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    comment = request.form.get("comment")
    with sqlite3.connect("database.db") as conn:
        conn.execute("INSERT INTO reviews (user_id, tool_id, comment) VALUES (?, ?, ?)",
                     (session["user_id"], tool_id, comment))
        conn.commit()
    flash("Review added.")
    return redirect(url_for("tool_detail", tool_id=tool_id))

def get_user_role(user_id):
    with sqlite3.connect("database.db") as conn:
        cur = conn.execute("SELECT role FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
    return row[0] if row else "user"

def is_admin():
    return session.get("user_id") and get_user_role(session["user_id"]) == "admin"

@app.route('/admin')
def admin():
    if not is_admin():
        flash("Admins only!")
        return redirect(url_for("home"))
    with sqlite3.connect("database.db") as conn:
        tools = conn.execute("SELECT * FROM tools ORDER BY id DESC").fetchall()
    return render_template("admin.html", tools=tools)

@app.route('/admin/delete/<int:tool_id>')
def delete_tool(tool_id):
    if not is_admin():
        flash("Admins only!")
        return redirect(url_for("home"))
    with sqlite3.connect("database.db") as conn:
        conn.execute("DELETE FROM tools WHERE id=?", (tool_id,))
        conn.commit()
    flash("Tool deleted.")
    return redirect(url_for("admin"))



if __name__ == '__main__':
    app.run(debug=True)



