from django.urls import path
from .views import *

urlpatterns = [
    # ======================
    # COURSES
    # ======================
    path('', course_list, name='courses'),
    path('add/', create_course, name='add_course'),

    # ======================
    # COURSE DETAIL & ENROLL
    # ======================
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/edit/', edit_course, name='edit_course'),
    path('courses/<int:course_id>/toggle/', toggle_course, name='toggle_course'),

    # ======================
    # LESSONS
    # ======================
    path('<int:course_id>/add-lesson/', add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/edit/', edit_lesson, name='edit_lesson'),
    path('lessons/<int:lesson_id>/toggle/', toggle_lesson, name='toggle_lesson'),
    path('lessons/<int:lesson_id>/complete/', complete_lesson, name='complete_lesson'),
]
