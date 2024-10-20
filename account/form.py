from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import UserModel

class RegistrationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ['full_name', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=128)