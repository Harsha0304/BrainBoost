from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CourseForm


@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    progress = course.progress_for_student(request.user)
    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'progress': progress
    })

@login_required
def create_course(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

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
