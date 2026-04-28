// ==================== ПЕРЕМЕННЫЕ ====================
let currentUserId = null;
let currentStudentId = null;

// ==================== МОДАЛЬНЫЕ ОКНА ====================
function openModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.add('active');
        showLogin();
        const passwordHint = document.getElementById('passwordHint');
        if (passwordHint) {
            passwordHint.style.color = '#666';
            passwordHint.innerHTML = 'Пароль должен быть не менее 8 символов';
        }
    }
}

function closeModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function showLogin() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm && registerForm) {
        loginForm.classList.remove('hidden-form');
        registerForm.classList.add('hidden-form');
    }
}

function showRegister() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm && registerForm) {
        loginForm.classList.add('hidden-form');
        registerForm.classList.remove('hidden-form');
    }
}

function checkPasswordStrength() {
    const password = document.getElementById('regPassword').value;
    const passwordHint = document.getElementById('passwordHint');

    if (password.length === 0) {
        passwordHint.style.color = '#666';
        passwordHint.innerHTML = 'Пароль должен быть не менее 8 символов';
    } else if (password.length < 8) {
        passwordHint.style.color = '#ff6b6b';
        passwordHint.innerHTML = 'Пароль слишком короткий! Нужно не менее 8 символов';
    } else {
        passwordHint.style.color = '#4caf50';
        passwordHint.innerHTML = '✓ Пароль подходит';
    }
}

// ==================== API: РЕГИСТРАЦИЯ ====================
function handleRegister(event) {
    event.preventDefault();

    const password = document.getElementById('regPassword').value;
    if (password.length < 8) {
        alert('Пароль должен содержать не менее 8 символов!');
        return;
    }

    const userData = {
        username: document.getElementById('regUsername').value,
        password: password,
        email: document.getElementById('regEmail').value,
        full_name: document.getElementById('regFullName').value,
        birth_date: document.getElementById('regBirthDate').value,
        parent_name: document.getElementById('regParentName').value,
        parent_phone: document.getElementById('regPhone').value,
        club_ids: []
    };

    const csrftoken = getCookie('csrftoken');
    fetch('/api/students/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (response.ok) {
            return response.json().then(data => {
                alert(`Регистрация успешна! Добро пожаловать, ${userData.username}!`);
                closeModal();
                showLogin();
            });
        } else {
            return response.json().then(data => {
                const errors = Object.values(data).flat().join('\n');
                alert('Ошибка регистрации:\n' + errors);
            });
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при регистрации');
    });
}

// ==================== API: ВХОД ====================
function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const csrftoken = getCookie('csrftoken');

    fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin',
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => {
        if (response.ok) {
            console.log('LOGIN OK');
            alert(`Добро пожаловать, ${username}!`);
            closeModal();

            // Сохраняем имя пользователя
            localStorage.setItem('username', username);

            // Получаем student_id по username и ПОТОМ перенаправляем
            fetchStudentByUsername(username);

            // Даем время сохраниться ID перед переходом
            setTimeout(() => {
                window.location.href = '/account/';
            }, 500);
        } else {
            alert('Неверное имя пользователя или пароль');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при входе');
    });
}

// ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function fetchStudentByUsername(username) {
    console.log('Ищем студента с username:', username);

    fetch('/api/students/')
        .then(response => response.json())
        .then(data => {
            console.log('Все студенты:', data);
            const students = data.results || data;
            // Ищем студента по username (без @, потому что в API username приходит без @)
            const cleanUsername = username.replace('@', '');
            const student = students.find(s => s.user?.username === username || s.user?.username === cleanUsername);

            if (student) {
                currentStudentId = student.id;
                currentUserId = student.user?.id;
                localStorage.setItem('studentId', currentStudentId);
                localStorage.setItem('userId', currentUserId);
                localStorage.setItem('username', username);
                console.log('Student ID сохранен:', currentStudentId);
                console.log('Username сохранен:', username);
            } else {
                console.error('Студент не найден для username:', username);
                console.log('Доступные username в API:', students.map(s => s.user?.username));
            }
        })
        .catch(error => console.error('Ошибка получения студента:', error));
}
// ==================== API: ЗАГРУЗКА КРУЖКОВ ИЗ БД ====================
function loadClubsFromAPI() {
    fetch('/api/clubs/')
        .then(response => response.json())
        .then(data => {
            // Поддерживает пагинацию DRF
            const clubs = data.results || data;
            displayClubs(clubs);
        })
        .catch(error => console.error('Ошибка загрузки кружков:', error));
}

function displayClubs(clubs) {
    const grid = document.querySelector('.activities-grid');
    if (!grid) return;

    // Очищаем сетку, но сохраняем заголовок если есть
    const title = document.querySelector('.page-title');
    grid.innerHTML = '';
    if (title) grid.appendChild(title);

    clubs.forEach(club => {
        const card = document.createElement('div');
        card.className = 'activity-card';
        card.onclick = () => showActivityInfoFromAPI(club.id);

        // Определяем иконку по названию кружка (можно расширить)
        const iconMap = {
            'изостудия': 'art.png',
            'игра на гитаре': 'guitar.png',
            'гитара': 'guitar.png',
            'робототехника': 'coala.png',
            'язык python для начинающих': 'python.png',
            'python': 'python.png',
            'театральная студия': 'theater.png',
            'театр': 'theater.png',
            'шахматы': 'chessboard.png'
        };
        const iconName = iconMap[club.name.toLowerCase()] || 'art.png';

        card.innerHTML = `
            <img src="/static/core/images/${iconName}" alt="${club.name}" class="activity-icon">
            <h3>${club.name}</h3>
            <div class="activity-age">${club.min_age}–${club.max_age} лет</div>
            <div class="activity-description">${club.description.substring(0, 100)}${club.description.length > 100 ? '...' : ''}</div>
            <div class="activity-seats">Свободно мест: ${club.available_seats} из ${club.total_seats}</div>
            <button class="btn-signup" onclick="event.stopPropagation(); openEnrollModal(${club.id}, '${club.name}')">Записаться ✒️</button>
        `;
        grid.appendChild(card);
    });
}

// ==================== API: ИНФОРМАЦИЯ О КРУЖКЕ ИЗ БД ====================
function showActivityInfoFromAPI(clubId) {
    fetch(`/api/clubs/${clubId}/`)
        .then(response => response.json())
        .then(club => {
            const infoContent = document.getElementById('infoContent');
            infoContent.innerHTML = `
                <h2>${club.name}</h2>
                <div class="info-section">
                    <h3>О кружке</h3>
                    <p>${club.description}</p>
                </div>
                <div class="info-section">
                    <h3>Возраст</h3>
                    <p>${club.min_age}–${club.max_age} лет</p>
                </div>
                <div class="info-section">
                    <h3>Преподаватель</h3>
                    <p><strong>${club.teacher?.full_name || 'Не указан'}</strong></p>
                    <p>${club.teacher?.info || ''}</p>
                </div>
                <div class="info-section">
                    <h3>Расписание</h3>
                    ${club.schedule && club.schedule.length > 0
                        ? `<ul class="schedule-list">${club.schedule.map(s => `<li>📌 ${getDayName(s.day_of_week)} ${s.start_time}–${s.end_time} (${s.room})</li>`).join('')}</ul>`
                        : '<p>Расписание уточняется</p>'}
                </div>
                <div class="info-section">
                    <h3>Места</h3>
                    <p>Занято: ${club.current_seats} / ${club.total_seats}</p>
                    <p>Свободно: ${club.available_seats}</p>
                </div>
            `;
            document.getElementById('infoModal').classList.add('active');
        })
        .catch(error => console.error('Ошибка загрузки информации о кружке:', error));
}

function getDayName(dayCode) {
    const days = {
        'Mon': 'Понедельник',
        'Tue': 'Вторник',
        'Wed': 'Среда',
        'Thu': 'Четверг',
        'Fri': 'Пятница',
        'Sat': 'Суббота',
        'Sun': 'Воскресенье'
    };
    return days[dayCode] || dayCode;
}

// ==================== API: ЗАПИСЬ НА КРУЖОК ====================
function openEnrollModal(clubId, clubName) {
    const studentId = localStorage.getItem('studentId');

    if (!studentId) {
        alert('Для записи на кружок необходимо войти в систему');
        openModal();
        return;
    }

    if (confirm(`Записаться на кружок "${clubName}"?`)) {
        enrollInClub(studentId, clubId, clubName);
    }
}

function enrollInClub(studentId, clubId, clubName) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/api/students/${studentId}/enroll/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ club_id: clubId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(`${data.message}`);
            // Обновляем список кружков, чтобы обновить счетчик мест
            loadClubsFromAPI();
        } else {
            alert(`Ошибка: ${data.error || 'Не удалось записаться'}`);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при записи');
    });
}

// ==================== ЗАКРЫТИЕ МОДАЛЬНЫХ ОКОН ====================
function closeInfoModal() {
    const infoModal = document.getElementById('infoModal');
    if (infoModal) {
        infoModal.classList.remove('active');
    }
}

// ==================== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ ====================
document.addEventListener('DOMContentLoaded', function() {
    // Загружаем кружки на странице activities.html
    if (window.location.pathname.includes('activities')) {
        loadClubsFromAPI();
    }

    // Восстанавливаем сессию, если есть сохраненные данные
    const savedStudentId = localStorage.getItem('studentId');
    if (savedStudentId) {
        currentStudentId = savedStudentId;
        currentUserId = localStorage.getItem('userId');
    }
});

// ==================== ОБРАБОТЧИКИ ЗАКРЫТИЯ ПО КЛИКУ НА ФОН ====================
window.onclick = function(event) {
    const authModal = document.getElementById('authModal');
    const infoModal = document.getElementById('infoModal');
    if (event.target === authModal) {
        closeModal();
    }
    if (event.target === infoModal) {
        closeInfoModal();
    }
}