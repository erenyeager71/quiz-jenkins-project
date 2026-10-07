import sys

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "quiz-demo-secret-key"

# In-memory "database" for the college demo: {email: {"password": hash, "last_score": int or None}}
USERS = {}

QUESTIONS = [
    {
        "text": "Which keyword is used to define a function in Python?",
        "options": ["func", "def", "function", "define"],
        "answer": 1,
    },
    {
        "text": "Which tool is commonly used for Continuous Integration?",
        "options": ["Jenkins", "Photoshop", "Excel", "Notepad"],
        "answer": 0,
    },
    {
        "text": "Which command uploads local commits to GitHub?",
        "options": ["git clone", "git pull", "git push", "git init"],
        "answer": 2,
    },
    {
        "text": "What does CI/CD stand for?",
        "options": [
            "Code Input / Code Delete",
            "Continuous Integration / Continuous Delivery",
            "Create Item / Create Document",
            "Compile Install / Compile Deploy",
        ],
        "answer": 1,
    },
]


def logged_in():
    return session.get("email") in USERS


def calculate_score():
    answers = session.get("answers", [])
    score = 0
    for i, q in enumerate(QUESTIONS):
        if i < len(answers) and answers[i] == q["answer"]:
            score += 1
    return score


@app.route("/")
def index():
    if logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            error = "Email and password are required."
        elif email in USERS:
            error = "This email is already registered. Please login."
        else:
            USERS[email] = {
                "password": generate_password_hash(password),
                "last_score": None,
            }
            return redirect(url_for("login", registered=1))
    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    message = None
    if request.args.get("registered"):
        message = "Signup successful! Please login."
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(email)
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["email"] = email
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error, message=message)


@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))
    email = session["email"]
    return render_template(
        "dashboard.html",
        email=email,
        last_score=USERS[email]["last_score"],
        total=len(QUESTIONS),
    )


@app.route("/start")
def start():
    if not logged_in():
        return redirect(url_for("login"))
    session["current"] = 0
    session["answers"] = []
    return redirect(url_for("quiz"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if not logged_in():
        return redirect(url_for("login"))
    if "current" not in session:
        return redirect(url_for("start"))

    current = session["current"]
    if current >= len(QUESTIONS):
        return redirect(url_for("result"))

    error = None
    if request.method == "POST":
        choice = request.form.get("option")
        if choice is None or not choice.isdigit() or int(choice) >= 4:
            error = "Please select an answer."
        else:
            answers = session.get("answers", [])
            answers.append(int(choice))
            session["answers"] = answers
            session["current"] = current + 1
            if session["current"] >= len(QUESTIONS):
                return redirect(url_for("result"))
            return redirect(url_for("quiz"))

    question = QUESTIONS[current]
    return render_template(
        "quiz.html",
        question=question,
        number=current + 1,
        total=len(QUESTIONS),
        error=error,
    )


@app.route("/result")
def result():
    if not logged_in():
        return redirect(url_for("login"))
    if session.get("current", 0) < len(QUESTIONS):
        return redirect(url_for("quiz") if "current" in session else url_for("start"))
    score = calculate_score()
    USERS[session["email"]]["last_score"] = score
    return render_template("result.html", score=score, total=len(QUESTIONS))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def run_jenkins_tests():
    """Automated, non-interactive test mode for Jenkins. Never starts a server."""
    app.config["TESTING"] = True
    USERS.clear()
    results = []
    state = {"score": None}

    email = "jenkins@test.com"
    password = "jenkins123"

    print("=================================")
    print("   JENKINS QUIZ TEST")
    print("=================================")
    print("")

    def check(name, func):
        try:
            ok = func()
        except Exception as exc:
            print("   (error: %s)" % exc)
            ok = False
        results.append(ok)
        print("Testing %s %s %s" % (name, "." * (20 - len(name)), "PASS" if ok else "FAIL"))

    with app.test_client() as client:

        def test_signup():
            page = client.get("/signup")
            if page.status_code != 200 or b"Sign Up" not in page.data:
                return False
            resp = client.post("/signup", data={"email": email, "password": password})
            return resp.status_code == 302 and email in USERS

        def test_login():
            page = client.get("/login")
            if page.status_code != 200:
                return False
            bad = client.post("/login", data={"email": email, "password": "wrong"})
            if bad.status_code != 200 or b"Invalid" not in bad.data:
                return False
            resp = client.post("/login", data={"email": email, "password": password})
            return resp.status_code == 302 and resp.headers["Location"].endswith("/dashboard")

        def test_dashboard():
            page = client.get("/dashboard")
            return page.status_code == 200 and b"Welcome to the Dashboard" in page.data

        def test_quiz():
            client.get("/start")
            for i, q in enumerate(QUESTIONS):
                page = client.get("/quiz")
                expected = ("Question %d of %d" % (i + 1, len(QUESTIONS))).encode()
                if page.status_code != 200 or expected not in page.data:
                    return False
                client.post("/quiz", data={"option": str(q["answer"])})
            return True

        def test_result():
            page = client.get("/result")
            expected = ("Your Score: %d / %d" % (len(QUESTIONS), len(QUESTIONS))).encode()
            if page.status_code != 200 or b"Quiz Completed!" not in page.data:
                return False
            if expected not in page.data:
                return False
            state["score"] = USERS[email]["last_score"]
            return True

        check("Signup", test_signup)
        check("Login", test_login)
        check("Dashboard", test_dashboard)
        check("Quiz", test_quiz)
        check("Result", test_result)

    print("")
    if all(results):
        print("Quiz Score: %d/%d" % (state["score"], len(QUESTIONS)))
        print("All tests passed successfully.")
        print("")
        print("Finished: SUCCESS")
        return 0
    print("Some tests failed.")
    print("")
    print("Finished: FAILURE")
    return 1


if __name__ == "__main__":
    if "--jenkins" in sys.argv:
        sys.exit(run_jenkins_tests())
    app.run(host="127.0.0.1", port=5000, debug=False)