from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.



class Sportsman(models.Model):
    """Спортсмен"""
    RANKS = [
        ('3', '3-й разряд'),
        ('2', '2-й разряд'),
        ('1', '1-й разряд'),
        ('kms', 'КМС'),
        ('ms', 'МС'),
        ('msmk', 'МСМК'),
    ]

    full_name = models.CharField('ФИО', max_length=255)
    birth_date = models.DateField('Дата рождения')
    rank = models.CharField('Разряд', max_length=10, choices=RANKS)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Спортсмен'
        verbose_name_plural = 'Спортсмены'


class Gym(models.Model):
    """Зал"""
    name = models.CharField('Название', max_length=255)
    address = models.CharField('Адрес', max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'


class Group(models.Model):
    """Группа"""
    name = models.CharField('Название группы', max_length=100)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='groups', verbose_name='Зал')
    sportsmen = models.ManyToManyField(Sportsman, through='GroupMembership', related_name='groups',
                                       verbose_name='Спортсмены')
    entrance_condition = models.TextField('Условие вступления', blank=True)

    def __str__(self):
        return f"{self.name} ({self.gym.name})"

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class GroupMembership(models.Model):
    """Участие спортсмена в группе (связующая таблица)"""
    sportsman = models.ForeignKey(Sportsman, on_delete=models.CASCADE, verbose_name='Спортсмен')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    joined_date = models.DateField('Дата вступления', default=timezone.now)

    class Meta:
        unique_together = ['sportsman', 'group']
        verbose_name = 'Членство в группе'
        verbose_name_plural = 'Членства в группах'


class Schedule(models.Model):
    """Расписание (РК - Расписание Команд?)"""
    WEEKDAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    name = models.CharField('Название тренировки', max_length=200)
    weekday = models.IntegerField('День недели', choices=WEEKDAYS)
    date = models.DateField('Конкретная дата', null=True, blank=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='schedules', verbose_name='Зал')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='schedules', verbose_name='Группа')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')

    def __str__(self):
        if self.date:
            return f"{self.name} - {self.date}"
        return f"{self.name} - {self.get_weekday_display()}"

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'


class Attendance(models.Model):
    """Посещаемость"""
    sportsman = models.ForeignKey(Sportsman, on_delete=models.CASCADE, verbose_name='Спортсмен')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='Расписание')
    is_present = models.BooleanField('Присутствие', default=False)
    note = models.TextField('Примечание', blank=True)

    class Meta:
        unique_together = ['sportsman', 'schedule']
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'


class Competition(models.Model):
    """Соревнование / РК (Рейтинговая комиссия?)"""
    name = models.CharField('Название соревнования', max_length=255)
    date = models.DateField('Дата проведения')
    location = models.CharField('Место проведения', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'


class Result(models.Model):
    """Результат спортсмена на соревновании (Статья, Стратегия, Победа, Отчёт)"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results',
                                    verbose_name='Соревнование')
    sportsman = models.ForeignKey(Sportsman, on_delete=models.CASCADE, related_name='results', verbose_name='Спортсмен')
    article = models.CharField('Статья/Дисциплина', max_length=200)
    strategy = models.CharField('Стратегия', max_length=200, blank=True)
    is_win = models.BooleanField('Победа', default=False)
    value = models.FloatField('Результат (сек/очки)', null=True, blank=True)
    report = models.TextField('Отчёт о выступлении', blank=True)

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        unique_together = ['competition', 'sportsman', 'article']


class Statistic(models.Model):
    """Статистика игроков (Норматив, Количество)"""
    sportsman = models.ForeignKey(Sportsman, on_delete=models.CASCADE, related_name='statistics',
                                  verbose_name='Спортсмен')
    norm = models.CharField('Норматив', max_length=100)
    quantity = models.FloatField('Количество')
    unit = models.CharField('Единица измерения', max_length=20, default='раз')
    date_recorded = models.DateField('Дата фиксации', default=timezone.now)

    def __str__(self):
        return f"{self.sportsman.full_name}: {self.norm} - {self.quantity} {self.unit}"

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистики'