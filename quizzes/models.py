from django.db import models
from django.conf import settings
from courses.models import Lesson

User = settings.AUTH_USER_MODEL

class Quiz(models.Model):
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"Quiz - {self.lesson.title}"

class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

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
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student} - {self.quiz} ({self.score})"


