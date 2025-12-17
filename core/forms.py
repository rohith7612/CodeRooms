from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Problem

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (Optional)'}),
        }

class CreateRoomForm(forms.ModelForm):
    TOPIC_CHOICES = [
        ('Random', 'Random'),
        ('Arrays', 'Arrays'),
        ('Strings', 'Strings'),
        ('Linked List', 'Linked List'),
        ('Stack', 'Stack'),
        ('Queue', 'Queue'),
        ('Trees', 'Trees'),
        ('Graphs', 'Graphs'),
        ('DP', 'Dynamic Programming'),
        ('Recursion', 'Recursion'),
    ]

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    topic = forms.ChoiceField(choices=TOPIC_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    passcode = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional Passcode'}))

    class Meta:
        model = Room
        fields = ['topic', 'difficulty', 'passcode']
