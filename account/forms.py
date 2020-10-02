from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# from .models import User
# from account.models import CustomUser


# class CustomUserCreationForm(UserCreationForm):

#     class Meta:
#         model = User
#         fields = '__all__'


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'login__input', 'placeholder': 'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'login__input', 'placeholder': 'Password'}))

    def clean(self):
        super().clean()
        data = self.cleaned_data
        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)
        if not user:
            u = User.objects.filter(username=username)
            if u.count() > 0:
                raise forms.ValidationError('Wrong Password')
            else:
                raise forms.ValidationError('Invalid Login')
        return self.cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=50, required=True,  widget=forms.TextInput(attrs={'class': 'register__input', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'register__input', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'register__input', 'placeholder': 'Confirm Password'}))

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1']
        )
        return user


class GuestRegisterationForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        super().clean()
        data = self.cleaned_data

        if data['password'] != data['confirm_password']:
            self.add_error('confirm_password', "Password doesn't match")

        u = User.objects.filter(username=data['username'])
        if u:
            self.add_error('username', 'This username is taken')


# def clean(self):
    #     super().clean()

    #     print('------------hiiiiiiiiii------------')
    #     data = self.cleaned_data
    #     print(data)

    # if 'g' in data['username']:
    #     # raise ValidationError("g is here")
    #     self.add_error('username', 'g is here')
    # if 'a' in data['email']:
    #     # raise ValidationError("g is here")
    #     self.add_error('email', 'g is here')
