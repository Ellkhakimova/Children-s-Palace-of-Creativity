from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Teacher, Club, Student, Schedule
from .serializers import (
    TeacherSerializer, ClubSerializer, StudentSerializer,
    StudentCreateSerializer, ScheduleSerializer, EnrollSerializer
)


class TeacherViewSet(viewsets.ModelViewSet):
    """
    API для преподавателей.
    GET /api/teachers/ - список всех
    GET /api/teachers/{id}/ - один преподаватель
    POST /api/teachers/ - создать
    PUT /api/teachers/{id}/ - обновить полностью
    PATCH /api/teachers/{id}/ - обновить частично
    DELETE /api/teachers/{id}/ - удалить
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]  # Пока открытый доступ


class ClubViewSet(viewsets.ModelViewSet):
    """
    API для кружков.
    GET /api/clubs/ - список всех
    GET /api/clubs/{id}/ - один кружок
    GET /api/clubs/available/ - только с свободными местами
    GET /api/clubs/{id}/schedule/ - расписание конкретного кружка
    """
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Эндпоинт: GET /api/clubs/available/
        Возвращает кружки, в которых есть свободные места
        """
        clubs_with_seats = []
        for club in Club.objects.all():
            if club.current_seats() < club.total_seats:
                clubs_with_seats.append(club)

        serializer = self.get_serializer(clubs_with_seats, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """
        Эндпоинт: GET /api/clubs/{id}/schedule/
        Возвращает расписание конкретного кружка
        """
        club = self.get_object()
        schedule = club.schedule_set.all()
        serializer = ScheduleSerializer(schedule, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API для расписания.
    GET /api/schedule/ - всё расписание
    GET /api/schedule/by_day/?day=Mon - по дням недели
    """
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_day(self, request):
        """
        Эндпоинт: GET /api/schedule/by_day/?day=Mon
        Возвращает расписание на конкретный день недели
        """
        day = request.query_params.get('day')
        if not day:
            return Response(
                {'error': 'Параметр "day" обязателен. Допустимые значения: Mon, Tue, Wed, Thu, Fri, Sat, Sun'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Приводим к формату, который хранится в БД
        day_upper = day.capitalize()
        schedule = Schedule.objects.filter(day_of_week=day_upper)
        serializer = self.get_serializer(schedule, many=True)
        return Response(serializer.data)




class StudentViewSet(viewsets.ModelViewSet):
    """
    API для студентов.
    GET /api/students/ - список всех
    GET /api/students/{id}/ - один студент
    POST /api/students/ - регистрация (использует StudentCreateSerializer)
    POST /api/students/{id}/enroll/ - запись на кружок
    GET /api/students/by_user/?user_id={id} - найти студента по user_id
    """
    queryset = Student.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer  # Для регистрации
        return StudentSerializer  # Для чтения

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """
        Эндпоинт: POST /api/students/{id}/enroll/
        Тело запроса: {"club_id": 1}
        Записывает студента на кружок с проверками
        """
        student = self.get_object()

        # Валидация входных данных
        serializer = EnrollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        club_id = serializer.validated_data['club_id']
        club = get_object_or_404(Club, id=club_id)

        # Проверка 1: Существует ли студент (уже есть, т.к. get_object)

        # Проверка 2: Возрастное ограничение
        if student.age < club.min_age:
            return Response(
                {'error': f'Слишком молод. Минимальный возраст для кружка: {club.min_age} лет'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if student.age > club.max_age:
            return Response(
                {'error': f'Слишком взрослый. Максимальный возраст для кружка: {club.max_age} лет'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка 3: Свободные места
        if club.current_seats() >= club.total_seats:
            return Response(
                {'error': f'В кружке "{club.name}" нет свободных мест'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка 4: Уже записан?
        if student.clubs.filter(id=club.id).exists():
            return Response(
                {'error': f'Вы уже записаны на кружок "{club.name}"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student.clubs.add(club)

        return Response({
            'status': 'success',
            'message': f'Вы успешно записаны на кружок "{club.name}"'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """GET /api/students/{id}/schedule/ - возвращает расписание студента на неделю"""
        student = self.get_object()

        # Получаем все кружки студента
        clubs = student.clubs.all()

        # Получаем всё расписание для этих кружков
        schedule_items = Schedule.objects.filter(club__in=clubs).select_related('club')

        # Дни недели в правильном порядке
        days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_names = {
            'Mon': 'Понедельник', 'Tue': 'Вторник', 'Wed': 'Среда',
            'Thu': 'Четверг', 'Fri': 'Пятница', 'Sat': 'Суббота', 'Sun': 'Воскресенье'
        }

        result = []
        for item in schedule_items:
            result.append({
                'day_of_week': item.day_of_week,
                'day_name': day_names.get(item.day_of_week, item.day_of_week),
                'start_time': item.start_time.strftime('%H:%M'),
                'end_time': item.end_time.strftime('%H:%M'),
                'room': item.room,
                'club_name': item.club.name,
                'club_id': item.club.id,
                'teacher_name': item.club.teacher.full_name if item.club.teacher else ''
            })

        # Сортируем по дням недели
        result.sort(key=lambda x: days_order.index(x['day_of_week']))

        return Response(result)

