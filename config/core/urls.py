from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TeacherViewSet, ClubViewSet, StudentViewSet, ScheduleViewSet
from . import views

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)  # /api/teachers/
router.register(r'clubs', ClubViewSet)  # /api/clubs/
router.register(r'students', StudentViewSet)  # /api/students/
router.register(r'schedule', ScheduleViewSet)  # /api/schedule/

urlpatterns = [
    # Страницы (должны быть ПЕРЕД api, чтобы не перехватывались)
    path('', views.index, name='index'),
    path('activities/', views.activities, name='activities'),
    path('account/', views.account, name='account'),

    # API маршруты
    path('api/', include(router.urls)),  # 👈 ВСЕ API ТЕПЕРЬ С ПРЕФИКСОМ api/
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api-auth/', include('rest_framework.urls')),
]
