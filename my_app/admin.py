from django.contrib import admin
from .models import (
    Sportsman, Gym, Group, GroupMembership,
    Schedule, Attendance, Competition, Result, Statistic
)

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1

@admin.register(Sportsman)
class SportsmanAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'birth_date', 'rank']
    list_filter = ['rank']
    search_fields = ['full_name']
    inlines = [GroupMembershipInline]

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'gym']
    list_filter = ['gym']
    filter_horizontal = ['sportsmen']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'gym', 'weekday', 'start_time']
    list_filter = ['gym', 'group', 'weekday']
    search_fields = ['name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['sportsman', 'schedule', 'is_present']
    list_filter = ['is_present', 'schedule__group']
    search_fields = ['sportsman__full_name']

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']
    list_filter = ['date']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['competition', 'sportsman', 'article', 'is_win', 'value']
    list_filter = ['competition', 'is_win']

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ['sportsman', 'norm', 'quantity', 'date_recorded']
    list_filter = ['norm', 'date_recorded']