from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TeacherViewSet, ClubViewSet, StudentViewSet, ScheduleViewSet, HomeworkAPIView
from . import views

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'clubs', ClubViewSet)
router.register(r'students', StudentViewSet)
router.register(r'schedule', ScheduleViewSet)

urlpatterns = [
    # Страницы
    path('', views.index, name='index'),
    path('activities/', views.activities, name='activities'),
    path('account/', views.account, name='account'),
    path('schedule/', views.schedule, name='schedule'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # API маршруты
    path('api/', include(router.urls)),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/homework/', HomeworkAPIView.as_view(), name='api_homework'),
]