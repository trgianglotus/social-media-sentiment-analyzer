from django_filters import FilterSet, filters
from .models import Student
from django.forms import DateInput, TextInput
from django.db import models
import django_filters 
from django import forms


class SearchBarWidget(forms.TextInput):
    class Media:
        css = {
            'all': ('templates/dashboard/search_bar.css',)
        }


class StudentFilter(FilterSet):
    class Meta:
        model = Student
        fields = {"name": ["contains"]}
        filter_overrides = {
             models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                'widget': SearchBarWidget(attrs={'placeholder': 'Search',})}
                },
            }


