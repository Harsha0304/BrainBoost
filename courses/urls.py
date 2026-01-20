from django.urls import path
from .views import (
    course_list,
    create_course,
    course_detail,
    enroll_course,
    add_lesson,
    lesson_detail,
    complete_lesson,
    download_certificate,
)

urlpatterns = [
    path('', course_list, name='courses'),
    path('add/', create_course, name='add_course'),

    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('<int:course_id>/certificate/', download_certificate, name='download_certificate'),

    path('<int:course_id>/add-lesson/', add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', complete_lesson, name='complete_lesson'),
]
