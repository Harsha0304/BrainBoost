from django.db import models
from django.conf import settings
from courses.models import Lesson

User = settings.AUTH_USER_MODEL


# =========================
# QUIZ (ONE PER LESSON)
# =========================
class Quiz(models.Model):
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)

    # quiz settings
    pass_percentage = models.PositiveIntegerField(default=60)
    time_limit_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Time limit in minutes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def total_questions(self):
        return self.questions.count()

    def __str__(self):
        return f"Quiz - {self.lesson.title}"


# =========================
# QUESTION
# =========================
class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()

    def __str__(self):
        return self.text


# =========================
# OPTIONS (MULTIPLE)
# =========================
class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


# =========================
# QUIZ RESULT
# =========================
class QuizResult(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_results'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='results'
    )

    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    percentage = models.FloatField()

    passed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return (
            f"{self.student} - {self.quiz} "
            f"({self.score}/{self.total_questions})"
        )
