from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from datetime import datetime, date
from .models import Sportsman, Group, GroupMembership, Gym, Schedule, Attendance, Statistic


def registration(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        birth_date = request.POST.get('birth_date')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'registration.html')

        user = User.objects.create_user(username=username, password=password)

        Sportsman.objects.create(
            user=user,
            full_name=full_name,
            birth_date=birth_date,
            rank='3'
        )

        login(request, user)
        messages.success(request, 'Регистрация прошла успешно!')
        return redirect('dashboard')

    return render(request, 'registration.html')


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')


@login_required
def dashboard(request):
    """Главная страница после входа"""
    teams_count = Group.objects.count()
    matches_count = Schedule.objects.filter(date__gte=date.today()).count()

    # Сегодняшняя посещаемость для текущего пользователя
    today_attendance = None
    if hasattr(request.user, 'sportsman'):
        today_attendance = Attendance.objects.filter(
            sportsman=request.user.sportsman,
            schedule__date=date.today()
        ).first()

    # Статистика посещаемости сегодня по всем
    today_schedules = Schedule.objects.filter(date=date.today())
    today_total_attendance = 0
    today_present_count = 0

    if today_schedules.exists():
        today_attendances = Attendance.objects.filter(schedule__in=today_schedules)
        today_total_attendance = today_attendances.count()
        today_present_count = today_attendances.filter(is_present=True).count()

    # Последние 5 тренировок
    recent_matches = Schedule.objects.all().order_by('-date')[:5]

    context = {
        'teams_count': teams_count,
        'matches_count': matches_count,
        'today_attendance': today_attendance,
        'today_total_attendance': today_total_attendance,
        'today_present_count': today_present_count,
        'today_attendance_rate': round(today_present_count / today_total_attendance * 100,
                                       1) if today_total_attendance > 0 else 0,
        'recent_matches': recent_matches,
    }
    return render(request, 'dashboard.html', context)


@login_required
def teams_list(request):
    """Список команд"""
    teams = Group.objects.all()
    context = {
        'teams': teams
    }
    return render(request, 'teams_list.html', context)


@login_required
def create_team(request):
    """Создание новой команды"""
    if request.method == 'POST':
        name = request.POST.get('name')
        gym_id = request.POST.get('gym')
        entrance_condition = request.POST.get('entrance_condition')

        if name and gym_id:
            gym = Gym.objects.get(id=gym_id)
            Group.objects.create(
                name=name,
                gym=gym,
                entrance_condition=entrance_condition
            )
            messages.success(request, f'Команда "{name}" создана!')
            return redirect('teams_list')
        else:
            messages.error(request, 'Заполните все обязательные поля')

    gyms = Gym.objects.all()
    context = {
        'gyms': gyms
    }
    return render(request, 'create_team.html', context)


@login_required
def matches_list(request):
    """Список матчей/тренировок"""
    matches = Schedule.objects.select_related('gym', 'group').all()
    context = {
        'my_matches': matches
    }
    return render(request, 'matches_list.html', context)


@login_required
def create_match(request):
    """Создание нового матча/тренировки"""
    if request.method == 'POST':
        name = request.POST.get('name')
        group_id = request.POST.get('group')
        gym_id = request.POST.get('gym')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if name and group_id and gym_id and date:
            try:
                group = Group.objects.get(id=group_id)
                gym = Gym.objects.get(id=gym_id)

                Schedule.objects.create(
                    name=name,
                    group=group,
                    gym=gym,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    weekday=0
                )
                messages.success(request, f'Матч "{name}" успешно создан!')
                return redirect('matches_list')
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
        else:
            messages.error(request, 'Заполните все обязательные поля')

    groups = Group.objects.all()
    gyms = Gym.objects.all()

    context = {
        'groups': groups,
        'gyms': gyms
    }
    return render(request, 'create_match.html', context)


@login_required
def statistics_view(request):
    """Статистика игроков"""
    statistics = Statistic.objects.select_related('sportsman').all().order_by('-date_recorded')

    # Агрегированная статистика по нормативам
    aggregated_stats = Statistic.objects.values('norm', 'unit').annotate(
        total_quantity=Sum('quantity'),
        sportsmen_count=Count('sportsman', distinct=True)
    )

    context = {
        'statistics': statistics,
        'aggregated_stats': aggregated_stats,
        'total_count': statistics.count(),
    }
    return render(request, 'statistics.html', context)


@login_required
def attendance_view(request):
    """Посещаемость с фильтрацией"""

    # Получаем параметры
    selected_schedule_id = request.GET.get('schedule', '')
    selected_sportsman_id = request.GET.get('sportsman', '')
    order_by = request.GET.get('order_by', '-schedule__date')

    # Базовый запрос
    attendances = Attendance.objects.select_related('sportsman', 'schedule').all()

    # Фильтры
    if selected_schedule_id:
        attendances = attendances.filter(schedule_id=selected_schedule_id)
    if selected_sportsman_id:
        attendances = attendances.filter(sportsman_id=selected_sportsman_id)

    # Сортировка
    if order_by == 'sportsman':
        attendances = attendances.order_by('sportsman__full_name')
    elif order_by == '-sportsman':
        attendances = attendances.order_by('-sportsman__full_name')
    elif order_by == 'schedule':
        attendances = attendances.order_by('schedule__name')
    elif order_by == '-schedule':
        attendances = attendances.order_by('-schedule__name')
    elif order_by == 'date':
        attendances = attendances.order_by('schedule__date')
    else:
        attendances = attendances.order_by('-schedule__date')

    attendances = attendances.order_by('-schedule__date')

    # Статистика по отфильтрованным данным
    total_attendances = attendances.count()
    present_count = attendances.filter(is_present=True).count()
    absent_count = total_attendances - present_count
    attendance_rate = (present_count / total_attendances * 100) if total_attendances > 0 else 0

    # Получаем все тренировки для фильтра
    schedules = Schedule.objects.all().order_by('-date')

    # Получаем всех спортсменов для фильтра
    sportsmen = Sportsman.objects.all().order_by('full_name')

    # Статистика по спортсменам (для отображения в таблице)
    sportsmen_stats = []
    for sportsman in sportsmen:
        sportsman_attendances = Attendance.objects.filter(sportsman=sportsman)
        if selected_schedule_id:
            sportsman_attendances = sportsman_attendances.filter(schedule_id=selected_schedule_id)

        total = sportsman_attendances.count()
        present = sportsman_attendances.filter(is_present=True).count()

        if total > 0:
            sportsmen_stats.append({
                'sportsman': sportsman,
                'total': total,
                'present': present,
                'absent': total - present,
                'rate': round(present / total * 100, 1) if total > 0 else 0
            })

    context = {
        'attendances': attendances,
        'total_attendances': total_attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': round(attendance_rate, 1),
        'schedules': schedules,
        'sportsmen': sportsmen,
        'selected_schedule_id': int(selected_schedule_id) if selected_schedule_id else '',
        'selected_sportsman_id': int(selected_sportsman_id) if selected_sportsman_id else '',
        'sportsmen_stats': sportsmen_stats,
    }
    return render(request, 'attendance.html', context)


@login_required
def add_attendance(request):
    """Отметить посещаемость"""
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule')
        sportsman_id = request.POST.get('sportsman')
        is_present = request.POST.get('is_present') == 'on'
        note = request.POST.get('note', '')

        if schedule_id and sportsman_id:
            schedule = get_object_or_404(Schedule, id=schedule_id)
            sportsman = get_object_or_404(Sportsman, id=sportsman_id)

            attendance, created = Attendance.objects.update_or_create(
                sportsman=sportsman,
                schedule=schedule,
                defaults={
                    'is_present': is_present,
                    'note': note
                }
            )
            messages.success(request, f'Посещаемость для {sportsman.full_name} отмечена!')
            return redirect('attendance')
        else:
            messages.error(request, 'Заполните все поля')

    # Получаем ВСЕ тренировки, не только будущие
    schedules = Schedule.objects.all().order_by('-date')

    # Если хотите только будущие, раскомментируйте:
    # schedules = Schedule.objects.filter(date__gte=date.today()).order_by('date')

    sportsmen = Sportsman.objects.all()

    print(f"DEBUG: Найдено тренировок: {schedules.count()}")  # Отладка
    for s in schedules:
        print(f"  - {s.name} ({s.date})")

    context = {
        'schedules': schedules,
        'sportsmen': sportsmen,
    }
    return render(request, 'add_attendance.html', context)


@login_required
def add_statistic(request):
    """Добавить новую запись статистики"""
    if request.method == 'POST':
        sportsman_id = request.POST.get('sportsman')
        norm = request.POST.get('norm')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')

        if sportsman_id and norm and quantity:
            sportsman = get_object_or_404(Sportsman, id=sportsman_id)
            Statistic.objects.create(
                sportsman=sportsman,
                norm=norm,
                quantity=float(quantity),
                unit=unit or 'раз'
            )
            messages.success(request, f'Статистика для {sportsman.full_name} добавлена!')
            return redirect('statistics')
        else:
            messages.error(request, 'Заполните все обязательные поля')

    sportsmen = Sportsman.objects.all()
    context = {
        'sportsmen': sportsmen,
    }
    return render(request, 'add_statistic.html', context)

@login_required
def sportsmen_list(request):
    """Список всех спортсменов"""
    sportsmen = Sportsman.objects.all()
    context = {
        'sportsmen': sportsmen
    }
    return render(request, 'sportsmen_list.html', context)


@login_required
def create_sportsman(request):
    """Создание нового спортсмена"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        birth_date = request.POST.get('birth_date')
        rank = request.POST.get('rank')

        if full_name and birth_date:
            sportsman = Sportsman.objects.create(
                full_name=full_name,
                birth_date=birth_date,
                rank=rank or '3'
            )
            messages.success(request, f'Спортсмен "{full_name}" добавлен!')
            return redirect('sportsmen_list')
        else:
            messages.error(request, 'Заполните обязательные поля')

    return render(request, 'create_sportsman.html')


@login_required
def group_detail(request, group_id):
    """Детальная информация о группе со списком спортсменов"""
    group = get_object_or_404(Group, id=group_id)
    members = group.sportsmen.all()

    other_sportsmen = Sportsman.objects.exclude(groups__id=group_id)

    context = {
        'group': group,
        'members': members,
        'other_sportsmen': other_sportsmen
    }
    return render(request, 'group_detail.html', context)


@login_required
def add_sportsman_to_group(request, sportsman_id):
    """Добавление спортсмена в группу (со страницы списка спортсменов)"""
    sportsman = get_object_or_404(Sportsman, id=sportsman_id)

    if request.method == 'POST':
        group_id = request.POST.get('group')

        if group_id:
            group = get_object_or_404(Group, id=group_id)

            if GroupMembership.objects.filter(sportsman=sportsman, group=group).exists():
                messages.warning(request, f'{sportsman.full_name} уже состоит в группе {group.name}')
            else:
                GroupMembership.objects.create(
                    sportsman=sportsman,
                    group=group
                )
                messages.success(request, f'{sportsman.full_name} добавлен в группу {group.name}')
                return redirect('sportsmen_list')
        else:
            messages.error(request, 'Выберите группу')

    groups = Group.objects.all()
    context = {
        'sportsman': sportsman,
        'groups': groups
    }
    return render(request, 'add_sportsman_to_group.html', context)


@login_required
def add_sportsman_to_group_form(request, group_id):
    """Добавление спортсмена в группу (со страницы деталей группы)"""
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        sportsman_id = request.POST.get('sportsman')

        if sportsman_id:
            sportsman = get_object_or_404(Sportsman, id=sportsman_id)

            if GroupMembership.objects.filter(sportsman=sportsman, group=group).exists():
                messages.warning(request, f'{sportsman.full_name} уже в группе {group.name}')
            else:
                GroupMembership.objects.create(
                    sportsman=sportsman,
                    group=group
                )
                messages.success(request, f'{sportsman.full_name} добавлен в группу {group.name}')
                return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, 'Выберите спортсмена')

    available_sportsmen = Sportsman.objects.exclude(groups__id=group.id)

    context = {
        'group': group,
        'available_sportsmen': available_sportsmen
    }
    # ИСПРАВЛЕНО: используем ТОТ ЖЕ шаблон add_sportsman_to_group.html
    return render(request, 'add_sportsman_to_group.html', context)


@login_required
def remove_sportsman_from_group(request, group_id, sportsman_id):
    """Удаление спортсмена из группы"""
    group = get_object_or_404(Group, id=group_id)
    sportsman = get_object_or_404(Sportsman, id=sportsman_id)

    GroupMembership.objects.filter(sportsman=sportsman, group=group).delete()
    messages.success(request, f'{sportsman.full_name} удален из группы {group.name}')

    return redirect('group_detail', group_id=group_id)