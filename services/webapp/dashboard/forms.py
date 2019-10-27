from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student


class NewStudentForm(forms.ModelForm):
    name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = Student
        fields = ['name']