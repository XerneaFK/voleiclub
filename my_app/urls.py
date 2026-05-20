from django.urls import path
from . import views

urlpatterns = [
    # Основные
    path('', views.dashboard, name='dashboard'),
    path('register/', views.registration, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Команды
    path('teams/', views.teams_list, name='teams_list'),
    path('teams/create/', views.create_team, name='create_team'),

    # Матчи
    path('matches/', views.matches_list, name='matches_list'),
    path('matches/create/', views.create_match, name='create_match'),

    # Статистика
    path('statistics/', views.statistics_view, name='statistics'),

    # Посещаемость
    path('attendance/', views.attendance_view, name='attendance'),

    # Спортсмены
    path('sportsmen/', views.sportsmen_list, name='sportsmen_list'),
    path('sportsmen/create/', views.create_sportsman, name='create_sportsman'),
    # Исправлено: add_sportsman_to_group_form вместо add_sportsman_to_group
    path('sportsmen/<int:sportsman_id>/add-to-group/', views.add_sportsman_to_group_form,
         name='add_sportsman_to_group'),

    # Группы (команды) - детали
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/add-sportsman/', views.add_sportsman_to_group_form, name='add_sportsman_to_group_form'),
    path('groups/<int:group_id>/remove/<int:sportsman_id>/', views.remove_sportsman_from_group,
         name='remove_sportsman_from_group'),

    # Статистика
    path('statistics/', views.statistics_view, name='statistics'),
    path('statistics/add/', views.add_statistic, name='add_statistic'),

    # Посещаемость
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
]