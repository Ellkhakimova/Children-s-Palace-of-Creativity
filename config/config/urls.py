from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('teachers.urls')), 
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create-assignment/', views.create_assignment, name='create_assignment')
]