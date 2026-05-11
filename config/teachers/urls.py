from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
]