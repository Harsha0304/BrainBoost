from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from collections import defaultdict

from courses.models import Course, Lesson, Enrollment, LessonProgress
from users.models import UserSession


@login_required
def dashboard(request):
    user = request.user

    # =======================
    # COURSE & PROGRESS DATA
    # =======================
    enrolled = Enrollment.objects.filter(student=user)
    enrolled_courses = Course.objects.filter(id__in=enrolled.values('course'))

    total_lessons = Lesson.objects.filter(course__in=enrolled_courses).count()
    completed_lessons = LessonProgress.objects.filter(
        student=user, completed=True
    ).count()

    progress = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    # =======================
    # TOTAL + LIVE TIME SPENT
    # =======================
    sessions = UserSession.objects.filter(user=user)

    total_seconds = 0
    for s in sessions:
        if s.logout_time:
            total_seconds += s.duration_seconds()
        else:
            # Active session
            total_seconds += (now() - s.login_time).total_seconds()

    time_spent_minutes = int(total_seconds // 60)

    # =======================
    # DAY-WISE TIME SPENT
    # =======================
    daily_time = defaultdict(int)

    for s in sessions:
        end_time = s.logout_time if s.logout_time else now()
        date_key = s.login_time.date()
        duration_minutes = int((end_time - s.login_time).total_seconds() // 60)
        daily_time[date_key] += duration_minutes

    daily_labels = [d.strftime("%d %b") for d in sorted(daily_time.keys())]
    daily_values = [daily_time[d] for d in sorted(daily_time.keys())]

    context = {
        'enrolled_courses': enrolled_courses,
        'enrolled_count': enrolled_courses.count(),
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress': progress,
        'time_spent_minutes': time_spent_minutes,

        # Graph data
        'daily_labels': daily_labels,
        'daily_values': daily_values,
    }

    return render(request, 'dashboard.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path('register/', include('users.urls')),
    path('courses/', include('courses.urls')),

    path('', dashboard, name='dashboard'),
]
