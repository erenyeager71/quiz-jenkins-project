"""
Quiz App - DevOps Demo
Normal mode : python quiz_app.py            (interactive, you type answers)
Jenkins mode: python quiz_app.py --jenkins  (automatic, no input needed)
"""

import argparse
import sys

# ---------------------------------------------------------------
# QUIZ CONTENT
# Replace these with your own questions if you want.
# "answer" is the number (1-4) of the correct option.
# ---------------------------------------------------------------
QUESTIONS = [
    {
        "question": "Which tool is used for continuous integration in this demo?",
        "options": ["Jenkins", "Photoshop", "Excel", "Notepad"],
        "answer": 1,
    },
    {
        "question": "Which command uploads local commits to GitHub?",
        "options": ["git clone", "git push", "git init", "git status"],
        "answer": 2,
    },
    {
        "question": "What does CI stand for in DevOps?",
        "options": [
            "Code Inspection",
            "Computer Interface",
            "Continuous Integration",
            "Central Infrastructure",
        ],
        "answer": 3,
    },
    {
        "question": "Which Python keyword is used to define a function?",
        "options": ["func", "function", "define", "def"],
        "answer": 4,
    },
    {
        "question": "Which file extension is used for Python source files?",
        "options": [".py", ".java", ".cpp", ".txt"],
        "answer": 1,
    },
]

# Jenkins mode answers (one per question, in order).
# By default it picks the correct answer for every question (5/5).
# To demo a lower score, change one number, e.g. replace the last one with 2.
AUTO_ANSWERS = [q["answer"] for q in QUESTIONS]

LINE = "=" * 30


def show_question(number, total, q):
    print()
    print("Question %d of %d" % (number, total))
    print(q["question"])
    for i, option in enumerate(q["options"], start=1):
        print("  %d. %s" % (i, option))


def get_user_choice(num_options):
    """Keep asking until the user enters a valid number. Never crashes."""
    while True:
        try:
            raw = input("Your answer (1-%d): " % num_options).strip()
        except EOFError:
            print("\nNo keyboard input available. Use: python quiz_app.py --jenkins")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nQuiz cancelled.")
            sys.exit(0)

        if raw.isdigit() and 1 <= int(raw) <= num_options:
            return int(raw)
        print("Invalid input. Please enter a number from 1 to %d." % num_options)


def check_answer(q, chosen):
    """Print feedback and return 1 if correct, else 0."""
    correct = q["answer"]
    if chosen == correct:
        print("Correct!")
        return 1
    print("Wrong! The correct answer is %d. %s" % (correct, q["options"][correct - 1]))
    return 0


def print_result(score, total):
    percentage = round(score / total * 100) if total else 0
    print()
    print(LINE)
    print("QUIZ COMPLETED".center(len(LINE)))
    print(LINE)
    print("Score: %d/%d" % (score, total))
    print("Percentage: %d%%" % percentage)
    print(LINE)


def run_interactive():
    print(LINE)
    print("PYTHON DEVOPS QUIZ".center(len(LINE)))
    print(LINE)
    total = len(QUESTIONS)
    score = 0
    for number, q in enumerate(QUESTIONS, start=1):
        show_question(number, total, q)
        chosen = get_user_choice(len(q["options"]))
        score += check_answer(q, chosen)
    print_result(score, total)


def run_jenkins():
    print(LINE)
    print("PYTHON DEVOPS QUIZ".center(len(LINE)))
    print("(Jenkins automatic mode)".center(len(LINE)))
    print(LINE)
    total = len(QUESTIONS)
    score = 0
    for number, q in enumerate(QUESTIONS, start=1):
        show_question(number, total, q)
        chosen = AUTO_ANSWERS[number - 1]
        print("Auto-selected answer: %d" % chosen)
        score += check_answer(q, chosen)
    print_result(score, total)


def main():
    parser = argparse.ArgumentParser(description="Python DevOps Quiz")
    parser.add_argument(
        "--jenkins",
        action="store_true",
        help="run automatically without keyboard input (for Jenkins)",
    )
    args = parser.parse_args()

    if args.jenkins:
        run_jenkins()
    else:
        run_interactive()


if __name__ == "__main__":
    main()