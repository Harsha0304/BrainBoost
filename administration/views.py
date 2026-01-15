from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from collections import defaultdict
from courses.models import Course, Lesson, Enrollment, LessonProgress
from users.models import UserSession
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from users.models import User
from django.utils.timezone import now, localdate
# Create your views here.

class UsernameEmailAuthBackend(ModelBackend):
    """Username or Email login"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Determine whether the username (Email) and password are correct"""
        query_set = User.objects.filter( Q(username=username) |  Q(email=username))
        try:
            if query_set.exists():
                user = query_set.get()
                if user.check_password(password):
                    return user
        except:
            return None
        return None

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

    today = localdate()

    today_sessions = UserSession.objects.filter(
        user=user,
        login_time__date=today
    )

    today_seconds = 0
    for s in today_sessions:
        end_time = s.logout_time if s.logout_time else now()
        today_seconds += (end_time - s.login_time).total_seconds()

    today_time_spent_minutes = int(today_seconds // 60)

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
        'time_spent_minutes': today_time_spent_minutes,

        # Graph data
        'daily_labels': daily_labels,
        'daily_values': daily_values,
    }

    return render(request, 'dashboard.html', context)