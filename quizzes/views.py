import random
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now

from courses.models import Lesson
from gamification.models import UserPoints, Badge, UserBadge
from .models import Quiz, Question, Option, QuizResult


# =========================
# CREATE QUIZ (FROM LESSON)
# =========================
@login_required
def create_quiz(request, lesson_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    lesson = get_object_or_404(Lesson, id=lesson_id)

    quiz, _ = Quiz.objects.get_or_create(
        lesson=lesson,
        defaults={'title': f"Quiz - {lesson.title}"}
    )

    return redirect('add_question', quiz_id=quiz.id)


# =========================
# ADD QUESTION (MANUAL)
# =========================
@login_required
def add_question(request, quiz_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_text = request.POST.get('question')
        options = request.POST.getlist('options')
        correct_index = request.POST.get('correct')

        if question_text and options and correct_index is not None:
            question = Question.objects.create(
                quiz=quiz,
                text=question_text
            )

            for index, option_text in enumerate(options):
                Option.objects.create(
                    question=question,
                    text=option_text,
                    is_correct=(str(index) == correct_index)
                )

        return redirect('add_question', quiz_id=quiz.id)

    return render(request, 'quizzes/add_question.html', {
        'quiz': quiz,
        'questions': quiz.questions.all()
    })

# =========================
# DOWNLOAD CSV TEMPLATE
# =========================
@login_required
def download_quiz_template(request, quiz_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quiz_template.csv"'

    writer = csv.writer(response)
    writer.writerow(['Question', 'Option1', 'Option2', 'CorrectOption(1/2)'])

    return response


# =========================
# BULK UPLOAD QUESTIONS
# =========================
@login_required
def bulk_upload_questions(request, quiz_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        decoded = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded)
        next(reader)  # skip header

        for row in reader:
            if len(row) != 4:
                continue

            question_text, opt1, opt2, correct = row

            question = Question.objects.create(
                quiz=quiz,
                text=question_text
            )

            Option.objects.create(question=question, text=opt1, is_correct=(correct == '1'))
            Option.objects.create(question=question, text=opt2, is_correct=(correct == '2'))

        return redirect('add_question', quiz_id=quiz.id)

    return redirect('add_question', quiz_id=quiz.id)


# =========================
# TAKE QUIZ (STUDENT)
# =========================
@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    questions = list(quiz.questions.prefetch_related('options'))
    random.shuffle(questions)
    questions = questions[:10]  # configurable limit

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


# =========================
# SUBMIT QUIZ
# =========================
@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    questions = quiz.questions.all()
    total_questions = questions.count()
    score = 0

    for question in questions:
        selected_option_id = request.POST.get(str(question.id))
        if selected_option_id:
            try:
                option = Option.objects.get(id=selected_option_id)
                if option.is_correct:
                    score += 1
            except Option.DoesNotExist:
                pass

    percentage = int((score / total_questions) * 100) if total_questions > 0 else 0
    passed = percentage >= quiz.pass_percentage

    # 🔥 FIX: PROVIDE ALL REQUIRED FIELDS
    QuizResult.objects.update_or_create(
        student=request.user,
        quiz=quiz,
        defaults={
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'passed': passed,
            'completed_at': now(),
        }
    )

    # Award gamification points for quiz completion
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    bonus = 20 if passed else 5
    user_points.add_points(score + bonus)
    for badge in Badge.objects.filter(points_required__lte=user_points.total_points):
        UserBadge.objects.get_or_create(user=request.user, badge=badge)

    return redirect('quiz_result', quiz_id=quiz.id)

@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    result = get_object_or_404(
        QuizResult,
        quiz=quiz,
        student=request.user
    )

    return render(request, 'quizzes/quiz_result.html', {
        'quiz': quiz,
        'result': result
    })
