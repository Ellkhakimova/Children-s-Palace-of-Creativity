# Добавь в начало views.py:
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Student
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Teacher, Assignment
from .forms import AssignmentForm
from django.contrib.auth import logout as auth_logout  

# Регистрация
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        full_name = data.get('full_name')
        birth_date = data.get('birth_date')
        parent_name = data.get('parent_name')
        parent_phone = data.get('parent_phone')

        # Проверка, существует ли пользователь
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Пользователь уже существует'}, status=400)

        # Создание пользователя
        user = User.objects.create_user(username=username, password=password, email=email)

        # Создание студента
        student = Student.objects.create(
            user=user,
            full_name=full_name,
            birth_date=birth_date,
            parent_name=parent_name,
            parent_phone=parent_phone
        )

        return JsonResponse({'success': True, 'message': 'Регистрация успешна'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Вход
@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({'success': True, 'message': 'Вход выполнен'})
        else:
            return JsonResponse({'error': 'Неверный логин или пароль'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Выход
def logout(request):
    auth_logout(request)
    return JsonResponse({'success': True, 'message': 'Выход выполнен'})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API для входа через fetch (универсальный для учеников и преподавателей)"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # Определяем роль пользователя
            role = 'student'
            role_id = None

            if hasattr(user, 'teacher_profile') and user.teacher_profile:
                role = 'teacher'
                role_id = user.teacher_profile.id
            elif hasattr(user, 'student'):
                role = 'student'
                role_id = user.student.id

            return JsonResponse({
                'success': True,
                'message': 'Вход выполнен',
                'role': role,
                'role_id': role_id,
                'username': user.username
            })
        else:
            return JsonResponse({'error': 'Неверный логин или пароль'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def activities(request):
    return render(request, 'core/activities.html')

def account(request):
    return render(request, 'core/account.html')

def schedule(request):
    return render(request, 'core/schedule.html')

def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    return render(request, 'core/teacher_dashboard.html', {'teacher': teacher})

@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    auth_logout(request)
    return JsonResponse({'success': True, 'message': 'Выход выполнен'})

@login_required
def create_assignment(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = teacher
            assignment.save()
            messages.success(request, 'Задание создано')
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    return render(request, 'core/create_assignment.html', {'form': form})