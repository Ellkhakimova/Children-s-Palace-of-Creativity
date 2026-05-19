from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    info = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    total_seats = models.IntegerField()

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def current_seats(self):
        return self.student_set.count()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=20)

    clubs = models.ManyToManyField(Club)

    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Подтверждено'),
        ('rejected', 'Отклонено'),
    ]
    application_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    achievements = models.TextField(blank=True, verbose_name='Достижения', help_text='Награды, грамоты, успехи ученика')

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        """Вычисляет возраст студента на основе даты рождения"""
        if not self.birth_date:
            return 0
        today = date.today()
        age = today.year - self.birth_date.year
        # Корректировка, если день рождения еще не наступил в этом году
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age


class Schedule(models.Model):
    DAYS = [
        ('Mon', 'Понедельник'),
        ('Tue', 'Вторник'),
        ('Wed', 'Среда'),
        ('Thu', 'Четверг'),
        ('Fri', 'Пятница'),
        ('Sat', 'Суббота'),
        ('Sun', 'Воскресенье'),
    ]

    day_of_week = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=20)

    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.club.name} - {self.day_of_week}"

class Homework(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='homeworks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homeworks')
    title = models.CharField(max_length=200, verbose_name='Тема')
    description = models.TextField(blank=True, verbose_name='Задание')
    due_date = models.DateField(null=True, blank=True, verbose_name='Срок сдачи')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['schedule', 'student']

    def __str__(self):
        return f'{self.schedule.club.name} - {self.student.full_name}'