from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # ADMIN: QUIZ CREATION
    #=========================
    path('lesson/<int:lesson_id>/create/',views.create_quiz,name='create_quiz'),
    path('quiz/<int:quiz_id>/add-question/',views.add_question,name='add_question'),
    path('quiz/<int:quiz_id>/bulk-upload/',views.bulk_upload_questions,name='bulk_upload_questions'),
    path('quiz/<int:quiz_id>/download-template/',views.download_quiz_template,name='download_quiz_template'),
    # =========================
    # STUDENT: TAKE QUIZ
    # =========================
    path('quiz/<int:quiz_id>/take/',views.take_quiz,name='take_quiz'),
    path('quiz/<int:quiz_id>/submit/',views.submit_quiz,name='submit_quiz'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),

]
