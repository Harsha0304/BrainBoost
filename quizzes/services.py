from gamification.models import UserPoints
from .models import QuizResult, Option

def evaluate_quiz(student, quiz, answers):
    """
    answers = {question_id: option_id}
    """
    score = 0

    for q_id, opt_id in answers.items():
        option = Option.objects.get(id=opt_id)
        if option.is_correct:
            score += 5

    QuizResult.objects.create(
        student=student,
        quiz=quiz,
        score=score
    )

    user_points = UserPoints.objects.get(user=student)
    user_points.total_points += score + 20
    user_points.update_level()

    return score
