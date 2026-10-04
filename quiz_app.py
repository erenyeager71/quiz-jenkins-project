questions = [
    {
        "question": "What is the capital of India?",
        "options": ["Delhi", "Mumbai", "Kolkata", "Chennai"],
        "answer": "Delhi"
    },
    {
        "question": "Which language is commonly used for web development?",
        "options": ["Python", "C++", "JavaScript", "All of these"],
        "answer": "All of these"
    },
    {
        "question": "Who invented Python?",
        "options": ["Guido van Rossum", "Bill Gates", "Elon Musk", "Mark Zuckerberg"],
        "answer": "Guido van Rossum"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"],
        "answer": "Pacific Ocean"
    }
]

score = 0

print("================================")
print("       DEVOPS QUIZ APP")
print("================================")

for question in questions:
    print("\n" + question["question"])

    for i, option in enumerate(question["options"], 1):
        print(f"{i}. {option}")

    selected_answer = question["answer"]

    print(f"Selected Answer: {selected_answer}")

    if selected_answer == question["answer"]:
        score += 1
        print("Result: Correct")
    else:
        print("Result: Incorrect")

print("\n================================")
print(f"FINAL SCORE: {score}/{len(questions)}")
print("================================")
