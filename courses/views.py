from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.db.models import Max

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
    if request.user.role == 'ADMIN':
        courses = Course.objects.all()
    else:
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
    if request.user.role == 'ADMIN':
        course = get_object_or_404(Course, id=course_id)
        lessons = course.lessons.all().order_by('order')
    else:
        course = get_object_or_404(Course, id=course_id, is_active=True)
        lessons = course.lessons.filter(is_active=True).order_by('order')

    enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

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
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course

            last_order = (
                Lesson.objects
                .filter(course=course)
                .aggregate(Max('order'))
                .get('order__max')
            )
            lesson.order = (last_order or 0) + 1

            if lesson.content_type == 'PDF':
                lesson.video_file = None
            elif lesson.content_type == 'VIDEO':
                lesson.pdf_file = None

            lesson.full_clean()
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
    lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)

    if not Enrollment.objects.filter(
        student=request.user,
        course=lesson.course
    ).exists():
        return redirect('course_detail', course_id=lesson.course.id)

    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    if lesson.content_type == 'PDF' and not progress.completed:
        progress.completed = True
        progress.completed_at = now()
        progress.save()

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'progress': progress
    })


@login_required
def edit_course(request, course_id):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'edit_course.html', {
        'form': form,
        'course': course
    })

@login_required
@require_POST
def toggle_course(request, course_id):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    course = get_object_or_404(Course, id=course_id)
    course.is_active = not course.is_active
    course.save(update_fields=['is_active'])

    return redirect('course_detail', course_id=course.id)

@login_required
def edit_lesson(request, lesson_id):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            updated_lesson = form.save(commit=False)

            # Lock course & order
            updated_lesson.course = course
            updated_lesson.order = lesson.order

            # Clean opposite file only if new one uploaded
            if updated_lesson.content_type == 'PDF' and request.FILES.get('pdf_file'):
                updated_lesson.video_file = None

            if updated_lesson.content_type == 'VIDEO' and request.FILES.get('video_file'):
                updated_lesson.pdf_file = None

            # Enforce model validation
            updated_lesson.full_clean()
            updated_lesson.save()

            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'edit_lesson.html', {
        'form': form,
        'lesson': lesson,
        'course': course
    })

@login_required
@require_POST
def toggle_lesson(request, lesson_id):
    if request.user.role != 'ADMIN':
        return redirect('courses')

    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.is_active = not lesson.is_active
    lesson.save(update_fields=['is_active'])

    return redirect('course_detail', course_id=lesson.course.id)

@login_required
@require_POST
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress = get_object_or_404(
        LessonProgress,
        student=request.user,
        lesson=lesson
    )

    if progress.completed:
        return JsonResponse({"status": "already_completed"})

    progress.completed = True
    progress.completed_at = now()
    progress.save()

    # 🎯 GAMIFICATION (ONCE)
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    user_points.add_points(10)

    badges = Badge.objects.filter(
        points_required__lte=user_points.total_points
    )
    for badge in badges:
        UserBadge.objects.get_or_create(
            user=request.user,
            badge=badge
        )

    return JsonResponse({"status": "completed"})
