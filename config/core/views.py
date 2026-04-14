# Добавь в начало views.py:
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Student


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


def api_login(request):
    """API для входа через fetch"""
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

from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def activities(request):
    return render(request, 'core/activities.html')

def account(request):
    return render(request, 'core/account.html')


from django.contrib.auth import logout as auth_logout

@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    auth_logout(request)
    return JsonResponse({'success': True, 'message': 'Выход выполнен'})