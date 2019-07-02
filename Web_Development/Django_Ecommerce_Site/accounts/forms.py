from django import forms
from django.contrib.auth import get_user_model

class GuestForm(forms.Form):
    email=forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':'form-control',
            'placeholder':'Your Email'
        })
    )

class ContactForm(forms.Form):
    fullname=forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Your full name'
        })
    )

class LoginForm(forms.Form):
    username=forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Your username'
        })
    )
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Your username'
        })
    )
class RegisterForm(forms.Form):
    username=forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Your username'
        })
    )
    email=forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':'form-control',
            'placeholder':'Your Email'
        })
    )
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Your password'
        })
    )
    password2=forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Confirm password'
        })
    )
    User=get_user_model()
    def clean_username(self):
        username=self.cleaned_data.get('username')
        qs=self.User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError('Username is taken')
        return username

    def clean(self):
        data=self.cleaned_data
        password=self.cleaned_data.get('password')
        password2=self.cleaned_data.get('password2')
        if password2 != password :
            raise forms.ValidationError('Passwords dont match')
        return data

