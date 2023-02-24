from django.contrib.auth.forms import UserCreationForm
from .models import ReserveUser, Booking, ParkingSpace
from django.forms import ModelForm
from django import forms
from django.utils import timezone




class RegisterForm(UserCreationForm, ModelForm):
    class Meta:
        model=ReserveUser
        fields=["username", "password1", "password2"]
        widgets={
            "username": forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'name', 'placeholder': 'Username'}),
            "password1":forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'pass1', 'placeholder': 'Password'}),
            "password2":forms.TextInput(attrs={'class': 'form-control form-control-lg', 'name' : 'pass2', 'placeholder': 'Confirm Password'})
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'checkout']
        widgets = {
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'checkout': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def clean(self):
        cleaned_data = super().clean()
        space = cleaned_data.get('space')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if space and check_in and check_out:
            if not space.is_available(check_in, check_out):
                raise forms.ValidationError('This space is not available for booking during the selected time period.')
            if check_out <= check_in:
                raise forms.ValidationError('Check-out time must be later than check-in time.')
        return cleaned_data