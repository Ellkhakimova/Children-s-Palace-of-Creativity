from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TeacherViewSet, ClubViewSet, StudentViewSet, ScheduleViewSet
from . import views

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)      # /api/teachers/
router.register(r'clubs', ClubViewSet)            # /api/clubs/
router.register(r'students', StudentViewSet)      # /api/students/
router.register(r'schedule', ScheduleViewSet)     # /api/schedule/

urlpatterns = [
    path('', views.index, name='index'),
    path('activities/', views.activities, name='activities'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]