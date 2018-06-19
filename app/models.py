import re
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from django.utils import timezone
from django.conf import settings
from django.core import validators

class Orientador(models.Model):
	nome = models.CharField('Nome', max_length=100, unique = True, validators=[validators.RegexValidator(re.compile('^[A-Z, ,´,Á-Ú]+$'),
            'O nome só pode conter letras', 'invalid')])

	def __str__(self):
		return self.nome

	class Meta:
		verbose_name='Orientador';
		verbose_name_plural='Orientadores'

	def save(self, force_insert=False, force_update=False):
		self.nome = self.nome.upper()
		super(Orientador, self).save(force_insert, force_update)


class Bolsista(models.Model):

	TIPO_CHOICES = (
	    (0, 'VOLUNTÁRIO'),
	    (1, 'REMUNERADO'),
	)


	nome = models.CharField('Nome', max_length=100, validators=[validators.RegexValidator(re.compile('^[A-Z, ,´,Á-Ú]+$'),
            'O nome só pode conter letras', 'invalid')])
	matricula = models.CharField('Matricula',max_length= 14,unique=True, validators=[MinLengthValidator(14),validators.RegexValidator(re.compile('^[\d]+$'),
            'A matrícula só pode conter números', 'invalid')])
	cartao_rfid = models.CharField('Cartão RFID', max_length=100, null=True, unique=True)
	orientador = models.ForeignKey(Orientador, verbose_name='Orientador', related_name='bolsista_professor', on_delete=models.CASCADE, default=True)
	tipo_bolsa = models.IntegerField('Tipo', choices=TIPO_CHOICES)
	carga_horaria_semanal = models.IntegerField('Carga Horaria (semanal)', validators=[MinValueValidator(1)])


	def __str__(self):
		return self.nome


	class Meta:
		verbose_name='Bolsista'
		verbose_name_plural='Bolsistas'

	def save(self, force_insert=False, force_update=False):
		self.nome = self.nome.upper()
		super(Bolsista, self).save(force_insert, force_update)

class Acesso(models.Model):
	bolsista = models.ForeignKey(Bolsista, verbose_name='Bolsista', related_name='bolsista_acesso', on_delete=models.CASCADE)
	data = models.DateField('Data Acesso', null=True, blank=True)
	atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
	hora_entrada = models.TimeField('Entrada', null=True, blank=True)
	hora_saida = models.TimeField('Saída', null = True, blank=True)
	total_horas = models.DurationField('Total', null = True, blank = True)



	class Meta:
	 	verbose_name = 'Acesso'
	 	verbose_name_plural = 'Acessos'

