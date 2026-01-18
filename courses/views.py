from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from .models import (
    Course,
    Lesson,
    Enrollment,
    LessonProgress
)
from .forms import CourseForm, LessonForm

from gamification.models import UserPoints, Badge, UserBadge


# =========================
# COURSE LIST
# =========================
@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses.html', {
        'courses': courses
    })


# =========================
# CREATE COURSE (ADMIN)
# =========================
@login_required
def create_course(request):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            return redirect('courses')
    else:
        form = CourseForm()

    return render(request, 'create_course.html', {
        'form': form
    })


# =========================
# COURSE DETAIL + ENROLLMENT
# =========================
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    lessons = course.lessons.filter(
        is_active=True
    ).order_by('order')

    enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'enrolled': enrolled
    })


# =========================
# ENROLL COURSE (STUDENT)
# =========================
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    return redirect('course_detail', course_id=course.id)


# =========================
# ADD LESSON (ADMIN)
# =========================
@login_required
def add_lesson(request, course_id):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()

    return render(request, 'add_lesson.html', {
        'form': form,
        'course': course
    })


# =========================
# LESSON DETAIL + COMPLETION + POINTS
# =========================
@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_active=True
    )

    # 🔒 Block access if not enrolled
    if not Enrollment.objects.filter(
        student=request.user,
        course=lesson.course
    ).exists():
        return redirect('course_detail', course_id=lesson.course.id)

    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    # =========================
    # MARK COMPLETED + GAMIFICATION
    # =========================
    if request.method == 'POST' and not progress.completed:
        progress.completed = True
        progress.completed_at = now()
        progress.save()

        # ⭐ POINTS LOGIC
        user_points, _ = UserPoints.objects.get_or_create(
            user=request.user
        )
        user_points.add_points(10)  # 10 points per lesson

        # 🏆 BADGE CHECK
        badges = Badge.objects.filter(
            points_required__lte=user_points.total_points
        )

        for badge in badges:
            UserBadge.objects.get_or_create(
                user=request.user,
                badge=badge
            )

        return redirect(
            'course_detail',
            course_id=lesson.course.id
        )

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'progress': progress
    })
