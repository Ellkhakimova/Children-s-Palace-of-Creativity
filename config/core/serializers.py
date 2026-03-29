from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import Teacher, Club, Student, Schedule


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'info', 'phone']

    def validate_phone(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Телефон слишком короткий")
        return value


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'room']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                "Время начала должно быть раньше времени окончания"
            )
        return data


class ClubSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    schedule = ScheduleSerializer(many=True, read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        source='teacher',
        write_only=True
    )
    current_seats = serializers.IntegerField(read_only=True)
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            'id', 'name', 'description', 'min_age', 'max_age',
            'total_seats', 'current_seats', 'available_seats',
            'teacher', 'teacher_id', 'schedule'
        ]

    def get_available_seats(self, obj):
        return obj.total_seats - obj.current_seats()

    def validate(self, data):
        if data['min_age'] > data['max_age']:
            raise serializers.ValidationError({
                'min_age': 'Минимальный возраст не может быть больше максимального'
            })
        if data['total_seats'] <= 0:
            raise serializers.ValidationError({
                'total_seats': 'Количество мест должно быть положительным'
            })
        if data['min_age'] < 0:
            raise serializers.ValidationError({
                'min_age': 'Возраст не может быть отрицательным'
            })
        if data['max_age'] > 18:
            raise serializers.ValidationError({
                'max_age': 'Максимальный возраст не может превышать 18 лет'
            })
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    clubs = ClubSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'full_name', 'birth_date', 'age',
            'parent_name', 'parent_phone',
            'clubs', 'application_status'
        ]


class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, min_length=3, max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)

    club_ids = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        source='clubs',
        write_only=True,
        many=True,
        required=False
    )

    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'username', 'password', 'email',
            'full_name', 'birth_date', 'age',
            'parent_name', 'parent_phone',
            'club_ids', 'application_status'
        ]

    def validate_birth_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Дата рождения не может быть в будущем")

        age = date.today().year - value.year
        if age > 18:
            raise serializers.ValidationError("Студент старше 18 лет не может зарегистрироваться")
        if age < 3:
            raise serializers.ValidationError("Ребенок младше 3 лет не может зарегистрироваться")
        return value

    def validate_parent_phone(self, value):
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) < 10:
            raise serializers.ValidationError("Введите корректный номер телефона")
        return value

    def validate_club_ids(self, value):
        if not value:
            return value
        for club in value:
            if club.current_seats() >= club.total_seats:
                raise serializers.ValidationError(
                    f"В кружке '{club.name}' нет свободных мест"
                )
        return value

    def validate(self, data):
        birth_date = data.get('birth_date')
        club_ids = data.get('clubs', [])

        if birth_date and club_ids:
            today = date.today()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1

            for club in club_ids:
                if age < club.min_age:
                    raise serializers.ValidationError(
                        f"Для кружка '{club.name}' минимальный возраст {club.min_age} лет. "
                        f"Ваш возраст: {age}"
                    )
                if age > club.max_age:
                    raise serializers.ValidationError(
                        f"Для кружка '{club.name}' максимальный возраст {club.max_age} лет. "
                        f"Ваш возраст: {age}"
                    )

        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': 'Пользователь с таким именем уже существует'
            })

        return data

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        clubs = validated_data.pop('clubs', [])

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        student = Student.objects.create(user=user, **validated_data)

        if clubs:
            student.clubs.set(clubs)

        return student


class EnrollSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()

    def validate_club_id(self, value):
        try:
            club = Club.objects.get(id=value)
        except Club.DoesNotExist:
            raise serializers.ValidationError("Кружок не найден")
        self.context['club'] = club
        return value