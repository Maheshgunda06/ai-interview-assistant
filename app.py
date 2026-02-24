from flask import Flask, render_template, request, redirect, session
import PyPDF2
import os
from textblob import TextBlob
import matplotlib.pyplot as plt
import os
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob
import PyPDF2
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Create Database
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Scores table
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score REAL
        )
    """)

    conn.commit()
    conn.close()
init_db()

# Home → Login Page
@app.route("/")
def home():
    return render_template("login.html")

# Register Page
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                  (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# Login System
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        session["user"] = username
        return redirect("/dashboard")
    else:
        return "Invalid Username or Password"
# Dashboard (Protected)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    else:
        return redirect("/")
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "user" in session:

        file = request.files["resume"]
        reader = PyPDF2.PdfReader(file)

        text = ""
        for page in reader.pages:
            text += page.extract_text()

        skills = []
        keywords = ["Python", "Java", "SQL", "Machine Learning",
                    "HTML", "CSS", "JavaScript", "React"]

        for word in keywords:
            if word.lower() in text.lower():
                skills.append(word)

        questions = []
        for skill in skills:
            questions.append(f"Explain your experience with {skill}")

        if not questions:
            questions.append("Tell me about your major projects.")

        return render_template("interview.html", questions=questions)

    else:
        return redirect("/")
@app.route('/interview', methods=['GET', 'POST'])
def interview():
    questions = []

    if request.method == 'POST':
        file = request.files['resume']

        if file:
            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                text += page.extract_text()

            # Simple keyword detection
            skills = []

            keywords = ["python", "java", "sql", "html", "css", "react", "flask"]

            for word in keywords:
                if word.lower() in text.lower():
                    skills.append(word.capitalize())

            if skills:
                for skill in skills:
                    questions.append(f"Explain your experience with {skill}.")
            else:
                questions.append("Tell me about your technical skills.")
                questions.append("What projects have you worked on?")

            session['questions'] = questions

    return render_template('interview.html', questions=session.get('questions', []))
# Evaluate Answer (NLP Scoring)
@app.route("/evaluate", methods=["POST"])
def evaluate():
    if "user" not in session:
        return redirect("/")

    answer = request.form["answer"]

    word_count = len(answer.split())

    from textblob import TextBlob
    blob = TextBlob(answer)
    sentiment = blob.sentiment.polarity

    score = round((word_count / 20) + (sentiment * 5), 2)

    # Save to database
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO scores (username, score) VALUES (?, ?)",
              (session["user"], score))
    conn.commit()
    conn.close()

    # RETURN INTERVIEW PAGE WITH SCORE
    return render_template("interview.html", score=score)
@app.route("/performance")
def performance():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()

    c.execute("SELECT score FROM scores WHERE username=?",
              (session["user"],))
    data = c.fetchall()
    conn.close()

    scores = [row[0] for row in data]

    badges = []

    if len(scores) >= 1:
        badges.append("🥉 First Interview Completed")

    if len(scores) >= 5:
        badges.append("🥈 5 Interviews Completed")

    if len(scores) > 0 and sum(scores)/len(scores) >= 8:
        badges.append("🥇 Excellent Performer")

    return render_template("performance.html",
                           scores=scores,
                           badges=badges)
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()

    c.execute("SELECT score FROM scores WHERE username=?", (session["user"],))
    scores = [row[0] for row in c.fetchall()]
    conn.close()

    total = len(scores)
    best = max(scores) if scores else 0
    avg = round(sum(scores)/len(scores), 2) if scores else 0

    return render_template("profile.html",
                           user=session["user"],
                           total=total,
                           best=best,
                           avg=avg)
@app.route('/generate', methods=['POST'])
def generate():
    file = request.files['resume']
    
    # Your resume processing logic here
    
    return redirect('/interview')
@app.route("/question-bank")
def question_bank():
    questions = {
        "Python": ["Explain OOP", "What is Flask?", "What is List Comprehension?"],
        "Java": ["Explain JVM", "What is OOPS?", "Difference between JDK & JRE?"],
        "SQL": ["What is JOIN?", "Explain Normalization", "What is Index?"]
    }
    return render_template("question_bank.html", questions=questions)
@app.route("/leaderboard")
def leaderboard():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT username, MAX(score) FROM scores GROUP BY username ORDER BY MAX(score) DESC")
    data = c.fetchall()
    conn.close()

    return render_template("leaderboard.html", data=data)
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/settings")
def settings():
    return render_template("settings.html")
# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)