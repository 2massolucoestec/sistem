from django import forms
from .models import Bolsista, Orientador, Acesso

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
