from django import forms
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_active']

class PlainFileInput(forms.FileInput):
    pass

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'title',
            'content',
            'content_type',
            'pdf_file',
            'video_file',
            'is_active',
        ]
        widgets = {
            'pdf_file': PlainFileInput(),
            'video_file': PlainFileInput(),
        }