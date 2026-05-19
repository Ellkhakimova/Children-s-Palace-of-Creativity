from django.contrib import admin
from .models import Teacher, Club, Student, Schedule

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone']
    search_fields = ['full_name']

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'min_age', 'max_age', 'total_seats']
    list_filter = ['teacher', 'min_age']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'birth_date', 'application_status', 'achievements']
    list_filter = ['application_status', 'clubs']
    search_fields = ['full_name', 'parent_name']
    filter_horizontal = ['clubs']  # Удобный виджет для ManyToMany
    fields = ['user', 'full_name', 'birth_date', 'parent_name', 'parent_phone', 'clubs', 'application_status',
              'achievements']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['club', 'day_of_week', 'start_time', 'end_time', 'room']
    list_filter = ['day_of_week', 'club']
