from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


# =========================
# COURSE
# =========================
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_courses'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_lessons(self):
        return self.lessons.filter(is_active=True).count()

    def __str__(self):
        return self.title


# =========================
# LESSON
# =========================
class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('PDF', 'PDF'),
        ('VIDEO', 'Video'),
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons'
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='PDF'
    )

    pdf_file = models.FileField(
        upload_to='lessons/pdfs/',
        null=True,
        blank=True
    )

    video_file = models.FileField(
        upload_to='lessons/videos/',
        null=True,
        blank=True
    )

    def clean(self):
        super().clean()

        if self.content_type == 'PDF':
            if not self.pdf_file:
                raise ValidationError('PDF file is required for PDF lessons.')
            if self.video_file:
                raise ValidationError('Remove video file for PDF lessons.')
            if not self.pdf_file.name.lower().endswith('.pdf'):
                raise ValidationError('Only PDF files are allowed.')

        elif self.content_type == 'VIDEO':
            if not self.video_file:
                raise ValidationError('Video file is required for video lessons.')
            if self.pdf_file:
                raise ValidationError('Remove PDF file for Video lessons.')
            if not self.video_file.name.lower().endswith(('.mp4', '.webm')):
                raise ValidationError('Only MP4/WebM videos are allowed.')

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']


# =========================
# ENROLLMENT
# =========================
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')


# =========================
# LESSON PROGRESS
# =========================
class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'lesson')


# =========================
# COURSE COMPLETION (NEW)
# =========================
class CourseCompletion(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='completed_courses'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} completed {self.course}"

class CourseCompletion(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}"
