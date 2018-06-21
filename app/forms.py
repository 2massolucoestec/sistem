from django import forms
from .models import Bolsista, Orientador, Acesso
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Usuário', min_length=4, max_length=150)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmação de Senha', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Usuário já existe")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email já existe")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Senha não corresponde")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user

class OrientadorForm(forms.ModelForm):
	class Meta:
		model = Orientador
		fields = ['nome']


class BolsistaForm(forms.ModelForm):
	class Meta:
		model = Bolsista
		fields = ['nome','matricula','cartao_rfid','orientador','tipo_bolsa','carga_horaria_semanal']
		readonly_fields=['cartao_rfid']

class AcessoForm(forms.ModelForm):
	class Meta:
		model = Acesso
		fields = ['bolsista']
