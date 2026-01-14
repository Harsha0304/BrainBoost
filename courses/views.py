from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson
from .forms import CourseForm, LessonForm

@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses.html', {'courses': courses})


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


# @login_required
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.order_by('order')
#     progress = course.progress_for_student(request.user)

#     return render(request, 'course_detail.html', {
#         'course': course,
#         'lessons': lessons,
#         'progress': progress
#     })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Only fetch lessons for now
    lessons = course.lessons.filter(is_active=True).order_by('order')

    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
    })

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

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    return render(request, 'lesson_detail.html', {
        'lesson': lesson
    })
