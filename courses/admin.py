from django.contrib import admin
from .models import Course, Lesson

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_active', 'created_at')
    inlines = [LessonInline]

admin.site.register(Lesson)

from .models import Enrollment, LessonProgress

admin.site.register(Enrollment)
admin.site.register(LessonProgress)
