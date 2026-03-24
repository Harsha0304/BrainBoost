from django.utils.timezone import now
from gamification.models import UserPoints
from .models import QuizResult, Option, Question


def evaluate_quiz(student, quiz, answers):
    """
    Evaluate a quiz submission.
    answers: {question_id: option_id}
    Returns the score (int).
    """
    questions = Question.objects.filter(quiz=quiz)
    total_questions = questions.count()
    score = 0

    for q_id, opt_id in answers.items():
        try:
            option = Option.objects.get(id=opt_id)
            if option.is_correct:
                score += 5
        except Option.DoesNotExist:
            pass

    percentage = int((score / total_questions) * 100) if total_questions else 0
    passed = percentage >= quiz.pass_percentage

    # BUG FIX: was missing total_questions, percentage, passed fields
    # and user_points.save() was never called
    QuizResult.objects.update_or_create(
        student=student,
        quiz=quiz,
        defaults={
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'passed': passed,
            'completed_at': now(),
        }
    )

    # Award gamification points
    user_points, _ = UserPoints.objects.get_or_create(user=student)
    user_points.total_points += score + 20
    user_points.update_level()
    user_points.save()  # BUG FIX: was never saved

    return score
