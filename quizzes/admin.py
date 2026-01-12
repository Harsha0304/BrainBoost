from django.contrib import admin
from .models import Quiz, Question, Option, QuizResult

class OptionInline(admin.TabularInline):
    model = Option
    extra = 2

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizResult)
