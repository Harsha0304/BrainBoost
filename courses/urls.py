from django.urls import path
from .views import (
    course_list,
    create_course,
    course_detail,
    enroll_course,
    add_lesson,
    lesson_detail,
    complete_lesson,
    edit_course,
    toggle_course,
    edit_lesson,
    toggle_lesson,
    download_certificate,
)

urlpatterns = [
    path('', course_list, name='courses'),
    path('add/', create_course, name='add_course'),

    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),

    # COURSE ADMIN
    path('<int:course_id>/edit/', edit_course, name='edit_course'),
    path('<int:course_id>/toggle/', toggle_course, name='toggle_course'),

    # LESSON ADMIN
    path('<int:course_id>/add-lesson/', add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', complete_lesson, name='complete_lesson'),
    path('lesson/<int:lesson_id>/edit/', edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/toggle/', toggle_lesson, name='toggle_lesson'),

    # CERTIFICATE
    path('<int:course_id>/certificate/', download_certificate, name='download_certificate'),
]
