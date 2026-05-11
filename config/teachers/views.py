# Create your views here.
from django.shortcuts import render, get_object_or_404
from core.models import Teacher   # модель осталась в core!

def teachers_list(request):
    """Страница со списком преподавателей"""
    teachers = Teacher.objects.all().prefetch_related('club_set')
    return render(request, 'teachers/teachers_list.html', {'teachers': teachers})

def teacher_detail(request, teacher_id):
    """Страница конкретного преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    clubs = teacher.club_set.all()
    return render(request, 'teachers/teacher_detail.html', {
        'teacher': teacher,
        'clubs': clubs
    })