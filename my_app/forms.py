from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Group, Schedule, Sportsman


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, label='ФИО')
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'full_name', 'birth_date', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'gym', 'entrance_condition']
        widgets = {
            'entrance_condition': forms.Textarea(attrs={'rows': 3}),
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['name', 'group', 'gym', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }