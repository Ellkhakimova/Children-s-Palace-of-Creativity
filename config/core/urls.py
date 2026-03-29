from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TeacherViewSet, ClubViewSet, StudentViewSet, ScheduleViewSet

# Создаем роутер для автоматической генерации URL
router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)      # /api/teachers/
router.register(r'clubs', ClubViewSet)            # /api/clubs/
router.register(r'students', StudentViewSet)      # /api/students/
router.register(r'schedule', ScheduleViewSet)     # /api/schedule/

urlpatterns = [
    path('', include(router.urls)),           # Все API эндпоинты
    path('api-auth/', include('rest_framework.urls')),  # Для логина в browsable API
]