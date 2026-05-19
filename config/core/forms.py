from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['student', 'title', 'description', 'due_date']
        labels = {
            'student': 'Ученик',
            'title': 'Задания',
            'description': 'Описание задания',
            'due_date': 'Срок сдачи',
        }
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': ''}),
        }