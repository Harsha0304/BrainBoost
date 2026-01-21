from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, localdate
from django.views.decorators.http import require_POST
from django.db.models import Max
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from .models import (
    Course,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseCompletion
)
from .forms import CourseForm, LessonForm

from gamification.models import UserPoints, Badge, UserBadge
from quizzes.models import Quiz, QuizResult   # 🔥 IMPORTANT


# =========================
# COURSE LIST
# =========================
@login_required
def course_list(request):
    if request.user.role == 'ADMIN':
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(is_active=True)

    return render(request, 'courses.html', {'courses': courses})


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

    return render(request, 'create_course.html', {'form': form})


# =========================
# COURSE DETAIL (🔥 QUIZ FIX)
# =========================
@login_required
def course_detail(request, course_id):
    if request.user.role == 'ADMIN':
        course = get_object_or_404(Course, id=course_id)
        lessons = course.lessons.all().order_by('order')
    else:
        course = get_object_or_404(Course, id=course_id, is_active=True)
        lessons = course.lessons.filter(is_active=True).order_by('order')

    enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    course_completed = CourseCompletion.objects.filter(
        student=request.user,
        course=course
    ).exists()

    # 🔥 QUIZ RESULT MAP (lesson_id → QuizResult)
    quiz_results = {}
    for lesson in lessons:
        if hasattr(lesson, 'quiz'):
            result = QuizResult.objects.filter(
                student=request.user,
                quiz=lesson.quiz
            ).first()
            quiz_results[lesson.id] = result

    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'enrolled': enrolled,
        'course_completed': course_completed,
        'quiz_results': quiz_results,   # 🔥 IMPORTANT
    })


# =========================
# ENROLL COURSE
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

            last_order = Lesson.objects.filter(
                course=course
            ).aggregate(Max('order'))['order__max']

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
# LESSON DETAIL
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

    # 🔥 Quiz result (if attempted)
    quiz_result = None
    if hasattr(lesson, 'quiz'):
        quiz_result = QuizResult.objects.filter(
            student=request.user,
            quiz=lesson.quiz
        ).first()

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'progress': progress,
        'quiz_result': quiz_result,  # 🔥 IMPORTANT
    })


# =========================
# COMPLETE LESSON
# =========================
@login_required
@require_POST
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    progress, _ = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    if progress.completed:
        return redirect('lesson_detail', lesson_id=lesson.id)

    progress.completed = True
    progress.completed_at = now()
    progress.save()

    # 🎯 Gamification
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    user_points.add_points(10)

    for badge in Badge.objects.filter(
        points_required__lte=user_points.total_points
    ):
        UserBadge.objects.get_or_create(
            user=request.user,
            badge=badge
        )

    # 🎓 Course completion
    course = lesson.course
    total = course.lessons.filter(is_active=True).count()
    completed = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course,
        completed=True
    ).count()

    if total > 0 and completed == total:
        CourseCompletion.objects.get_or_create(
            student=request.user,
            course=course
        )
        return redirect('course_detail', course_id=course.id)

    return redirect('lesson_detail', lesson_id=lesson.id)


# =========================
# DOWNLOAD CERTIFICATE
# =========================
@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not CourseCompletion.objects.filter(
        student=request.user,
        course=course
    ).exists():
        return redirect('course_detail', course_id=course.id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{course.title}_certificate.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 1.5 * inch,
                          "Certificate of Completion")

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(width / 2, height - 2.5 * inch,
                          "This is to certify that")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 3.3 * inch,
                          request.user.get_full_name()
                          or request.user.username)

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(width / 2, height - 4.2 * inch,
                          "has successfully completed the course")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, height - 5.1 * inch,
                          course.title)

    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 6.2 * inch,
                          f"Date: {localdate()}")

    pdf.setFont("Helvetica-Oblique", 12)
    pdf.drawCentredString(width / 2, 1.5 * inch,
                          "BrainBoost Learning Platform")

    pdf.showPage()
    pdf.save()
    return response
