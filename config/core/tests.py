from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, time, timedelta
from .models import Teacher, Club, Student, Schedule


class APITestCase(TestCase):
    """Полный тест API"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = APIClient()

        # Создаем преподавателя
        self.teacher = Teacher.objects.create(
            full_name="Тестовый Преподаватель",
            info="Опытный педагог",
            phone="+7(999)123-45-67"
        )

        # Создаем кружок
        self.club = Club.objects.create(
            name="Тестовый кружок",
            description="Для тестирования",
            min_age=7,
            max_age=15,
            total_seats=10,
            teacher=self.teacher
        )

        # Создаем расписание
        self.schedule = Schedule.objects.create(
            club=self.club,
            day_of_week='Mon',
            start_time=time(16, 0),
            end_time=time(18, 0),
            room="Кабинет №1"
        )

        # Создаем пользователя
        self.user = User.objects.create_user(
            username='teststudent',
            password='testpass123',
            email='test@example.com'
        )

        # Создаем студента
        self.student = Student.objects.create(
            user=self.user,
            full_name="Тестовый Студент",
            birth_date=date(2015, 5, 15),  # 9 лет
            parent_name="Родитель",
            parent_phone="+7(999)777-88-99",
            application_status='pending'
        )

    def test_get_clubs_list(self):
        """Тест: получение списка кружков"""
        response = self.client.get('/api/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Пагинация

    def test_get_club_detail(self):
        """Тест: получение одного кружка"""
        response = self.client.get(f'/api/clubs/{self.club.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Тестовый кружок")

    def test_get_available_clubs(self):
        """Тест: получение кружков со свободными местами"""
        response = self.client.get('/api/clubs/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Есть свободные места

    def test_get_schedule_by_day(self):
        """Тест: получение расписания по дню недели"""
        response = self.client.get('/api/schedule/by_day/?day=Mon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_registration_valid(self):
        """Тест: успешная регистрация студента"""
        data = {
            'username': 'newstudent',
            'password': 'newpass123',
            'email': 'new@example.com',
            'full_name': 'Новый Студент',
            'birth_date': '2015-06-20',
            'parent_name': 'Родитель Нового',
            'parent_phone': '+7(999)111-22-33',
            'club_ids': [self.club.id]
        }
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_registration_invalid_age(self):
        """Тест: регистрация с некорректным возрастом"""
        data = {
            'username': 'oldstudent',
            'password': 'oldpass123',
            'email': 'old@example.com',
            'full_name': 'Старый Студент',
            'birth_date': '1990-01-01',  # Слишком старый
            'parent_name': 'Родитель',
            'parent_phone': '+7(999)111-22-33',
            'club_ids': [self.club.id]
        }
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enroll_in_club(self):
        """Тест: запись на кружок"""
        response = self.client.post(f'/api/students/{self.student.id}/enroll/', {
            'club_id': self.club.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что студент записался
        self.student.refresh_from_db()
        self.assertEqual(self.student.clubs.count(), 1)

    def test_enroll_twice(self):
        """Тест: повторная запись на тот же кружок"""
        # Первая запись
        self.client.post(f'/api/students/{self.student.id}/enroll/', {
            'club_id': self.club.id
        }, format='json')

        # Вторая запись (должна быть ошибка)
        response = self.client.post(f'/api/students/{self.student.id}/enroll/', {
            'club_id': self.club.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enroll_age_too_young(self):
        """Тест: запись слишком молодого студента"""
        young_student = Student.objects.create(
            user=User.objects.create_user(username='young', password='pass'),
            full_name="Молодой",
            birth_date=date(2020, 1, 1),  # 4 года (слишком молод для кружка 7+)
            parent_name="Родитель",
            parent_phone="+7(999)000-00-00",
            application_status='pending'
        )

        response = self.client.post(f'/api/students/{young_student.id}/enroll/', {
            'club_id': self.club.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_profile_by_user_id(self):
        """Тест: получение профиля по user_id"""
        response = self.client.get(f'/api/students/by_user/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], "Тестовый Студент")