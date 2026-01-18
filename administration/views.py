from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, localdate
from collections import defaultdict
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend

from courses.models import Course, Lesson, Enrollment, LessonProgress
from users.models import UserSession, User
from gamification.models import UserPoints


# =========================
# USERNAME / EMAIL LOGIN
# =========================
class UsernameEmailAuthBackend(ModelBackend):
    """Username or Email login"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None


# =========================
# DASHBOARD VIEW
# =========================
@login_required
def dashboard(request):
    user = request.user

    # 🔥 Ensure streak is updated for today
    user.update_streak()

    # =======================
    # COURSE & PROGRESS DATA
    # =======================
    enrolled = Enrollment.objects.filter(student=user)
    enrolled_courses = Course.objects.filter(
        id__in=enrolled.values('course')
    )

    total_lessons = Lesson.objects.filter(
        course__in=enrolled_courses
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        student=user,
        completed=True
    ).count()

    progress = int(
        (completed_lessons / total_lessons) * 100
    ) if total_lessons else 0

    # =======================
    # TODAY TIME SPENT
    # =======================
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
    sessions = UserSession.objects.filter(user=user)
    daily_time = defaultdict(int)

    for s in sessions:
        end_time = s.logout_time if s.logout_time else now()
        date_key = s.login_time.date()
        duration_minutes = int(
            (end_time - s.login_time).total_seconds() // 60
        )
        daily_time[date_key] += duration_minutes

    sorted_days = sorted(daily_time.keys())[-7:]
    daily_labels = [d.strftime("%d %b") for d in sorted_days]
    daily_values = [daily_time[d] for d in sorted_days]

    context = {
        # Courses
        'enrolled_courses': enrolled_courses,
        'enrolled_count': enrolled_courses.count(),

        # Progress
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress': progress,

        # Time
        'time_spent_minutes': today_time_spent_minutes,

        # 🔥 Streak
        'current_streak': user.current_streak,
        'longest_streak': user.longest_streak,

        # Graph
        'daily_labels': daily_labels,
        'daily_values': daily_values,
    }

    return render(request, 'dashboard.html', context)


# =========================
# LEADERBOARD VIEW
# =========================
@login_required
def leaderboard(request):
    leaderboard_data = (
        UserPoints.objects
        .select_related('user')
        .order_by('-total_points', '-level')[:10]
    )

    return render(request, 'leaderboard.html', {
        'leaderboard': leaderboard_data
    })
