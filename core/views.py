import os
import json
from dotenv import load_dotenv

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import QuizProgress
from .ai_helper import ai_conversation, check_grammar  # ← import dari ai_helper

load_dotenv()

# ======================================
# DASHBOARD UTAMA 
# ======================================
@login_required(login_url="login")
def dashboard_view(request):
    progress, created = QuizProgress.objects.get_or_create(user=request.user)
    
    accuracy = 0
    if progress.total_quiz > 0:
        accuracy = int((progress.correct_answers / progress.total_quiz) * 100)
        
    context = {
        "progress": progress,
        "accuracy": accuracy,
    }
    return render(request, "dashboard.html", context)


# ======================================
# LOGIN
# ======================================
def login_view(request):
    if request.method == "POST":
        username_input = request.POST.get("username")
        password = request.POST.get("password")
        user = None

        if "@" in username_input:
            try:
                user_obj = User.objects.get(email=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_input, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name} 👋")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("dashboard")
        else:
            messages.error(request, "Username/email atau password salah.")

    return render(request, "login.html")


# ======================================
# REGISTER
# ======================================
def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not username or not email or not password:
            messages.error(request, "Semua field wajib diisi.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect("register")

        username = username.strip()
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah digunakan.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname
        )

        QuizProgress.objects.create(
            user=user,
            score=0,
            total_quiz=0,
            correct_answers=0,
            topic_stats={}
        )

        messages.success(request, "Registrasi berhasil! Silakan login. 🎉")
        return redirect("login")

    return render(request, "register.html")


# ======================================
# LOGOUT
# ======================================
@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "Berhasil logout.")
    return redirect("login")


# ======================================
# GRAMMAR CHECKER
# ======================================
@login_required(login_url="login")
def grammar_view(request):
    result = None
    user_text = ""

    if request.method == "POST":
        user_text = request.POST.get("text", "").strip()

        if user_text:
            response = check_grammar(user_text)  # ← pakai ai_helper

            if response["success"]:
                data = response["data"]
                result = {
                    "original": user_text,
                    "corrected": data.get("corrected", user_text),
                    "errors": data.get("errors", []),
                    "score": data.get("score", 100),
                    "feedback": data.get("feedback", ""),
                }
            else:
                result = {
                    "original": user_text,
                    "corrected": "Gagal menganalisis.",
                    "errors": [],
                    "score": 0,
                    "feedback": response["message"],
                }

    return render(request, "grammar.html", {
        "result": result,
        "user_text": user_text
    })


# ======================================
# AI CHAT
# ======================================
@login_required(login_url="login")
def chat_view(request):
    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if user_message:
            history = request.session["chat_history"]
            history.append({
                "sender": "user",
                "text": user_message
            })

            response = ai_conversation(user_message)  # ← pakai ai_helper

            ai_response = response["message"]  # sukses atau gagal, selalu ada "message"

            history.append({
                "sender": "ai",
                "text": ai_response
            })

            request.session.modified = True

    context = {
        "chat_history": request.session["chat_history"]
    }

    return render(request, "chat.html", context)


# ======================================
# QUIZ DATA
# ======================================
QUIZ_DATA = [
    {
        "topic": "Business",
        "question": 'What does the word "Resilient" mean?',
        "options": ["A. Easily broken or damaged", "B. Very attractive and charming", "C. Able to recover quickly from difficulties", "D. Moving at a very fast pace"],
        "answer": "C"
    },
    {
        "topic": "Business",
        "question": 'What does the idiom "Break the ice" mean?',
        "options": ["A. Start a friendly conversation", "B. Destroy something cold", "C. Become angry", "D. End a relationship"],
        "answer": "A"
    },
    {
        "topic": "Business",
        "question": 'What does the word "Ambitious" mean?',
        "options": ["A. Lazy", "B. Having strong goals and determination", "C. Easily bored", "D. Very shy"],
        "answer": "B"
    },
    {
        "topic": "Business",
        "question": 'What does the idiom "Piece of cake" mean?',
        "options": ["A. A dessert", "B. Something expensive", "C. Something very easy", "D. Something impossible"],
        "answer": "C"
    },
    {
        "topic": "Business",
        "question": 'What does the word "Reliable" mean?',
        "options": ["A. Can be trusted", "B. Dangerous", "C. Expensive", "D. Nervous"],
        "answer": "A"
    },
    {
        "topic": "Travel",
        "question": 'What does the idiom "Hit the books" mean?',
        "options": ["A. Throw books away", "B. Buy books", "C. Study hard", "D. Write a novel"],
        "answer": "C"
    },
    {
        "topic": "Travel",
        "question": 'What does the word "Generous" mean?',
        "options": ["A. Selfish", "B. Willing to give and share", "C. Angry", "D. Dishonest"],
        "answer": "B"
    },
    {
        "topic": "Travel",
        "question": 'What does the idiom "Spill the beans" mean?',
        "options": ["A. Cook food", "B. Reveal a secret", "C. Waste money", "D. Make a joke"],
        "answer": "B"
    },
    {
        "topic": "Travel",
        "question": 'What does the word "Confident" mean?',
        "options": ["A. Believing in your abilities", "B. Easily scared", "C. Very angry", "D. Uncertain"],
        "answer": "A"
    },
    {
        "topic": "Travel",
        "question": 'What does the idiom "Under the weather" mean?',
        "options": ["A. Feeling sick", "B. Traveling abroad", "C. Feeling excited", "D. Going outside"],
        "answer": "A"
    }
]


# ======================================
# QUIZ
# ======================================
@login_required(login_url="login")
def quiz_view(request):
    progress, created = QuizProgress.objects.get_or_create(user=request.user)
    current_question = int(request.GET.get("q", 0))

    if current_question >= len(QUIZ_DATA):
        return redirect("progress")

    quiz = QUIZ_DATA[current_question]
    selected_answer = None
    is_correct = False

    if request.method == "POST":
        selected_answer = request.POST.get("answer")
        answered_session_key = f"answered_q_{current_question}"
        
        if not request.session.get(answered_session_key, False):
            progress.total_quiz += 1
            
            topic = quiz.get("topic", "Business")
            
            if not progress.topic_stats:
                progress.topic_stats = {}
            if topic not in progress.topic_stats:
                progress.topic_stats[topic] = {"correct": 0, "total": 0}
                
            progress.topic_stats[topic]["total"] += 1

            if selected_answer == quiz["answer"]:
                progress.score += 10
                progress.correct_answers += 1
                is_correct = True
                progress.topic_stats[topic]["correct"] += 1
                
            progress.save()
            request.session[answered_session_key] = True
        else:
            if selected_answer == quiz["answer"]:
                is_correct = True

    context = {
        "progress": progress,
        "quiz": quiz,
        "question_number": current_question + 1,
        "total_questions": len(QUIZ_DATA),
        "next_question": current_question + 1,
        "selected_answer": selected_answer,
        "is_correct": is_correct
    }

    return render(request, "quiz.html", context)


# ======================================
# PROGRESS
# ======================================
@login_required(login_url="login")
def progress_view(request):
    progress, created = QuizProgress.objects.get_or_create(user=request.user)
    accuracy = 0

    if progress.total_quiz > 0:
        accuracy = int((progress.correct_answers / progress.total_quiz) * 100)

    topic_data = []
    db_topics = progress.topic_stats if progress.topic_stats else {}
    
    target_topics = ["Business", "Travel"]
    for t in target_topics:
        if t in db_topics and db_topics[t]["total"] > 0:
            calc_score = int((db_topics[t]["correct"] / db_topics[t]["total"]) * 100)
        else:
            calc_score = 0  
        topic_data.append({"name": t, "score": calc_score})

    badges = []
    if progress.total_quiz > 0:
        badges.append("First Quiz")
    if progress.total_quiz >= 7:
        badges.append("7 Day Streak")
    if accuracy >= 80 and progress.total_quiz > 0:
        badges.append("Top Scorer")

    context = {
        "progress": progress,
        "accuracy": accuracy,
        "topic_data": topic_data,
        "badges": badges
    }

    return render(request, "progress.html", context)


# ======================================
# RESET PROGRESS
# ======================================
@login_required(login_url="login")
def reset_progress_view(request):
    if request.method == "POST":
        progress = QuizProgress.objects.get(user=request.user)
        progress.score = 0
        progress.total_quiz = 0
        progress.correct_answers = 0
        progress.topic_stats = {}
        progress.save()
        
        # Clear all quiz session keys
        keys_to_delete = [key for key in request.session.keys() if key.startswith('answered_q_')]
        for key in keys_to_delete:
            del request.session[key]
        request.session.modified = True
        
        messages.success(request, "Progress berhasil direset! 🎉")
        return redirect("progress")
    
    return redirect("progress")


# ======================================
# CLEAR CHAT
# ======================================
@login_required(login_url="login")
def clear_chat_view(request):
    if request.method == "POST":
        request.session["chat_history"] = []
        request.session.modified = True
        messages.success(request, "Chat history berhasil dihapus! 🗑️")
        return redirect("chat")
    
    return redirect("chat")