from django.contrib.auth.forms import UserCreationForm
from .models import ReserveUser
from django.forms import ModelForm
from django import forms



class RegisterForm(UserCreationForm, ModelForm):
    class Meta:
        model=ReserveUser
        fields=["username", "password1", "password2"]
        widgets={
            "username": forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'name', 'placeholder': 'Username'}),
            "password1":forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'pass1', 'placeholder': 'Password'}),
            "password2":forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'pass2', 'placeholder': 'Confirm Password'})
        }