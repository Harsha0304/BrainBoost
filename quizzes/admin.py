from django.contrib import admin
from .models import Quiz, Question, Option, QuizResult


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('text', 'quiz')
    search_fields = ('text',)


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson')
    search_fields = ('title',)


class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'completed_at')
    list_filter = ('quiz',)


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizResult, QuizResultAdmin)
