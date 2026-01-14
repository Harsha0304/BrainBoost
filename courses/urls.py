from django.urls import path
from .views import (
    course_list,
    create_course,
    course_detail,
    add_lesson,
    lesson_detail
)

urlpatterns = [
    path('', course_list, name='courses'),
    path('add/', create_course, name='add_course'),
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/add-lesson/', add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
]
