from django.http import JsonResponse
import serial
import json
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .forms import OrientadorForm, BolsistaForm, AcessoForm, UserForm, CustomUserCreationForm
from .models import Orientador, Bolsista, Acesso
from datetime import datetime, time, date, timedelta
import datetime
from django.utils import timezone
from django.template.loader import get_template
from django.urls import resolve
from django.http import HttpResponse
from django.db.models import Sum
from django.views.generic import View
from app.utils import render_to_pdf #created in step 4
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

from django.contrib.auth.decorators import user_passes_test

def list_usuario(request):
	usuarios = User.objects.all()
	return render(request, 'usuario/list_usuario.html',{'usuarios':usuarios})

@login_required(login_url='/login')
def edit_usuario(request, pk):
	usuario = User.objects.get(pk=pk)
	form = CustomUserCreationForm(request.POST, instance=request.user)

	if form.is_valid():
		form.save()
		return redirect('app:list_usuario')
	return render(request,"registrar.html",{'form':form})


@login_required(login_url='/login')
def edit_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('edit_password')
        else:
            messages.error(request, 'Não foi possível alterar a senha!')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'usuario/edit_password.html', {
        'form': form
    })

@login_required(login_url='/login')
def edit_user(request, template_name="usuario/edit_username.html"):
	if request.method == "POST":
#		user = request.user
		form = UserForm(request.POST, instance = request.user)
		if form.is_valid():
			user = form.save(commit=False)
			user.save()
			return redirect('/')
	else:
		form = UserForm(instance=request.user)
    
	return render(request,template_name, {'form':form} )


@user_passes_test(lambda u: u.is_superuser)
def registrar(request):
	if request.method == 'POST':
		f = UserCreationForm(request.POST)
		if f.is_valid():
			f.save()
			messages.success(request, 'Usuário cadastrado com sucesso!')
			return redirect('/register')

	else:
        	f = UserCreationForm()

	return render(request, 'registrar.html', {'form': f})



class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        acessos = Acesso.objects.all()
        data = {
        	'acessos': acessos,

        }
        pdf = render_to_pdf('pdf/invoice.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response
#Login e Home
def logar(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			login(request,form.get_user())
			return redirect('app:home')
		else:
			return render(request,"login.html",{"form":form})
	return render(request, "login.html", {"form":AuthenticationForm()})

def relatorio_op(request):
	return render(request, 'acesso/relatorio_op.html')

def modal(request):
	return render(request, 'basemodal.html')

def modalt(request):
	return render(request, 'baset.html')


@login_required(login_url='/login')
def home(request):
	if request.user.is_superuser:
		
		return render(request, 'home_admin.html')
	else:
		bolsistas = Bolsista.objects.all()
		return render(request, 'home_user_comum.html',{'bolsistas':bolsistas})

#def home_professor(request):
#	template_name = 'professor/home_professor.html'
#	context = {}
#	return render(request, template_name, context)

#Professor
@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def create_orientador(request):
	form = OrientadorForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('app:list_orientador')

	return render(request, 'orientador/cad_orientador.html',{'form':form})


@login_required(login_url='/login')
def update_orientador(request, pk):
	orientador = Orientador.objects.get(pk=pk)
	form = OrientadorForm(request.POST or None, instance = orientador)

	if form.is_valid():
		form.save()
		return redirect('app:list_orientador')
	return render(request,'orientador/cad_orientador.html',{'form':form})


@login_required(login_url='/login')
def list_orientador(request):
	orientadores = Orientador.objects.all()
	return render(request, 'orientador/list_orientador.html',{'orientadores':orientadores})


@login_required(login_url='/login')
def delete_orientador(request, pk):
	try:
		orientador = Orientador.objects.get(pk=pk)
		if request.method == 'POST':
			orientador.delete()
			return redirect('app:list_orientador')
	except Orientador.DoesNotExist:
		return redirect('app:home')
	return render(request,'orientador/confirm_delete_orientador.html',{'orientador':orientador})

#Bolsista
def home_bolsista(request):
	template_name = 'bolsista/home_bolsista.html'
	context = {}
	return render(request, template_name, context)


@login_required(login_url='/login')
def create_bolsista(request):
	form = BolsistaForm(request.POST or None)
	form.fields['cartao_rfid'].widget.attrs['readonly'] = True
	if form.is_valid():
		form.save()
		return redirect('app:list_bolsista')
	return render(request, 'bolsista/cad_bolsista.html', {'form':form})


@login_required(login_url='/login')
def update_bolsista(request, pk):
	bolsista = Bolsista.objects.get(pk=pk)
	form = BolsistaForm(request.POST or None, instance = bolsista)
	if form.is_valid():
		form.save()
		return redirect('app:list_bolsista')
	return render(request,'bolsista/cad_bolsista.html',{'form':form})


@login_required(login_url='/login')
def list_bolsista(request):
	bolsistas = Bolsista.objects.all()
	return render(request, 'bolsista/list_bolsista.html',{'bolsistas':bolsistas})


@login_required(login_url='/login')
def delete_bolsista(request, pk):
	try:
		bolsista = Bolsista.objects.get(pk=pk)
		if request.method == 'POST':
			bolsista.delete()
			return redirect('app:list_bolsista')
	except Bolsista.DoesNotExist:
		return redirect('app:home')
	return render(request,'bolsista/confirm_delete_bolsista.html',{'bolsista':bolsista})


#Acesso
@login_required(login_url='/login')
def create_ac(request):
	bolsistas = Bolsista.objects.all()
	return render(request, 'acesso/cad_acesso.html',{'bolsistas':bolsistas})



@login_required(login_url='/login')
def list_acesso(request):
	acessos = Acesso.objects.all()
	return render(request, 'acesso/list_acesso.html',{'acessos':acessos})

def test_acesso(request, pk):
	try:

		bolsista = Bolsista.objects.get(pk=pk)
		acesso = Acesso.objects.filter(bolsista=bolsista).order_by('-id').first()
		if acesso is not None:

			if acesso.hora_saida == None:
				acesso.hora_saida = timezone.localtime(timezone.now()).time()
				acesso.total_horas = timedelta(hours = acesso.hora_saida.hour, minutes=acesso.hora_saida.minute, seconds=acesso.hora_saida.second) - timedelta(hours = acesso.hora_entrada.hour, minutes=acesso.hora_entrada.minute, seconds=acesso.hora_entrada.second)
				acesso.save()
				redirect('app:list_acesso')
			else:
				novo_acesso = Acesso()
				novo_acesso.bolsista =  bolsista
				novo_acesso.data = date.today()
				novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
				novo_acesso.save()
				redirect('app:list_acesso')
		else:
			novo_acesso = Acesso()
			novo_acesso.bolsista =  bolsista
			novo_acesso.data = date.today()
			novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
			novo_acesso.save()
			redirect('app:list_acesso')
	except Bolsista.DoesNotExist:
		redirect('app:list_acesso')
	acessos = Acesso.objects.all()
	return render(request, 'acesso/list_acesso.html', {'acessos':acessos})


def acesso_bolsista(request, pk):
	try:
		bolsista = Bolsista.objects.get(pk=pk)
		acessos = Acesso.objects.filter(bolsista=bolsista)
	except Bolsista.DoesNotExist:
		return redirect('app:home')
	return render(request,'acesso/list_bolsista.html',{'acessos':acessos})

def ac(request):
	bolsistas = Bolsista.objects.all()
	return render(request, 'acesso/acesso_bolsista.html',{'bolsistas':bolsistas})

def act(request):
	bolsistas = Bolsista.objects.all()
	return render(request, 'acesso/acesso_bolsistat.html',{'bolsistas':bolsistas})


#def ap(request):
#	if request.method == 'POST':
#		if request.POST['data_'] == '':
#			return redirect ('app:list_acesso')
#		else:
#			return redirect(reverse('app:list', args=(request.POST['data_'], request.POST['data_f'])))
#	return render(request, 'acesso/acesso_periodo.html',{})

##def ap(request):
#	if request.method == 'POST':
#		if request.POST['data_'] == '':
#			return redirect ('app:list_acesso')
#		else:
#			return redirect(reverse('app:RelatorioPeriodo', args=(request.POST['data_'], request.POST['data_f'])))
#	return render(request, 'acesso/acesso_periodo.html',{})

def ap(request):
	data = str(date.today())
	if request.method == 'POST':
		pk = request.POST.get('select_bolsista')
		return redirect(reverse('app:RelatorioPeriodoB', args=(request.POST['data_'],request.POST['data_f'],request.POST['select_bolsista'])))
	bolsistas = Bolsista.objects.all()
	return render(request, 'acesso/relatorio.html',{'bolsistas':bolsistas, 'data':data,})

def apb(request):
	if request.method == 'POST':
		pk = request.POST.get('select_bolsista')
		return redirect(reverse('app:RelatorioPeriodoB', args=(request.POST['data_'],request.POST['data_f'],request.POST['select_bolsista'])))
	bolsistas = Bolsista.objects.all()

	return render(request, 'acesso/relatorio.html',{'bolsistas':bolsistas})


class RelatorioPeriodoB(View):
	def get(self, request, data_ini, data_fim, pk):
		if not pk == '0':
			bolsista = Bolsista.objects.get(pk=pk)
			acessos = Acesso.objects.filter(data__range=(data_ini,data_fim), bolsista = bolsista).exclude(hora_saida=None)
			titulo = '%s' %(bolsista.nome)
			is_todos = '0'

		else:
			bolsista = Bolsista.objects.all()
			acessos = Acesso.objects.filter(data__range=(data_ini,data_fim)).exclude(hora_saida=None)
			titulo = 'TODOS BOLSISTAS'
			is_todos = '1'

#		bolsistas = Bolsista.objects.get(pk=pk)

#		acessos = Acesso.objects.filter(data__range=(data_ini,data_fim))

		if acessos.exists():
			th = acessos.aggregate(total=Sum('total_horas'))
		else:
			th='--'
#		th = acessos.aggregate(total=Sum('total_horas'))
		d1 = datetime.datetime.strptime(data_ini, "%Y-%m-%d").date()
		d2 = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
		data = {
			'acessos':acessos,
			'th':th,
			'bolsistas':bolsista,
			'data_inicio':d1.strftime("%d/%m/%Y"),
			'data_fim':d2.strftime("%d/%m/%Y"),
			'titulo': titulo,
			'is_todos':is_todos,
		}
		pdf = render_to_pdf('pdf/relatorio_periodo.html',data)
		response = HttpResponse(pdf,content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename=RelatorioPeriodoBolsista.pdf'
		return response


def list(request, data_ini, data_fim):
	acessos = Acesso.objects.filter(data__range=(data_ini, data_fim))
	return render(request,'acesso/list_ap.html',{'acessos':acessos})


class RelatorioBolsista(View):
    def get(self, request, pk, **kwargs):
        bolsista = Bolsista.objects.get(pk=pk)
        acessos = Acesso.objects.filter(bolsista=bolsista).exclude(hora_saida=None)
        if acessos.exists():
        	th = acessos.aggregate(total=Sum('total_horas'))
        else:
        	th='--'
        data = {
        	'bolsista': bolsista,
        	'acessos': acessos,
        	'th': th,
        }
        pdf = render_to_pdf('pdf/invoice.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=Relatório %s.pdf'%(bolsista.nome)
        return response

class RelatorioPeriodo(View):
	def get(self, request, data_ini, data_fim):
		acessos = Acesso.objects.filter(data__range=(data_ini,data_fim))

		#th = acessos.aggregate(total=Sum('total_horas'))
		if acessos.exists():
			th = acessos.aggregate(total=Sum('total_horas'))
		else:
			th='--'
		d1 = datetime.datetime.strptime(data_ini, "%Y-%m-%d").date()
		d2 = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
		data = {
			'acessos':acessos,
			'th':th,
			'data_inicio':d1.strftime("%d/%m/%Y"),
			'data_fim':d2.strftime("%d/%m/%Y"),
		}
		pdf = render_to_pdf('pdf/relatorio_periodo.html',data)
		response = HttpResponse(pdf,content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename=RelatorioPeriodo.pdf'
		return response




@login_required(login_url='/login')
def create_bolsista2(request):
	path = "/dev/ttyACM0"
	baudrate = 9600
	con_serial = serial.Serial(path, baudrate)
	form = BolsistaForm(request.POST or None)
	try:
		while True:
			if(con_serial.readline() != ""):
				key_value = str(con_serial.readline())
				for i in range(len(key_value)):
					key_value = key_value.replace("b\'","")
				
				for i in range(len(key_value)):
					key_value = key_value.replace("\'", "")

				for i in range(len(key_value)):
					key_value = key_value.replace("\\r\\n", "")

		
		
		if form.is_valid():
			bolsista = form.save(commit = False)
			bolsista.cartao_rfid = key_value
			bolsista.save()
			return redirect('app:list_bolsista')
		return render(request, 'bolsista/cad_bolsista.html', {'form':form})
		#return render(request, 'teste.html', {'key_value':key_value})
	except serial.SerialException as e:
		return render(request, 'teste.html', {'key_value':e})
	finally:
		con_serial.close()
	
@login_required(login_url='/login')
def create_bolsista3(request):
	return render(request, 'bolsista/cad_test.html', {})

def t(request):
	d = request.POST.get('nome')
	return render(request, 'bolsista/cad_.html', {'d':d})

def teste_ajax(request, id_):
	idx = "Id recebido via AJAX: " + id_
	message = "Apresente o Cartão RFID"
	data = {

		'text': idx,
		'valu': "ttt",
	}
	return HttpResponse(json.dumps(data), content_type='application/json')

#def teste_aja(request):
#	idx = "Id recebido via AJAX: "
#	message = "Apresente o Cartão RFID"
#	dx = {
#
#		'text': idx,
#		'valu': "ttt",
#	}
#	return HttpResponse(json.dumps(dx), content_type='application/json')

def teste_aja(request):
	path = "/dev/ttyACM0"
	baudrate = 9600
	con_serial = serial.Serial(path, baudrate)
	try:
		while True:
			if(con_serial.readline() != ""):
				key_value = str(con_serial.readline())
				for i in range(len(key_value)):
					key_value = key_value.replace("b\'","")
				
				for i in range(len(key_value)):
					key_value = key_value.replace("\'", "")

				for i in range(len(key_value)):
					key_value = key_value.replace("\\r\\n", "")
				dx = {
					'key_value':key_value
				}
				return HttpResponse(json.dumps(dx), content_type='application/json')
		#return render(request, 'teste.html', {'key_value':key_value})
	except serial.SerialException as e:
		return render(request, 'teste.html', {'key_value':e})
	finally:
		con_serial.close()



def teste_aja2(request):
	path = "/dev/ttyACM0"
	baudrate = 9600
	con_serial = serial.Serial(path, baudrate)
	try:
		while True:
			if(con_serial.readline() != ""):
				key_value = str(con_serial.readline())
				for i in range(len(key_value)):
					key_value = key_value.replace("b\'","")
				
				for i in range(len(key_value)):
					key_value = key_value.replace("\'", "")

				for i in range(len(key_value)):
					key_value = key_value.replace("\\r\\n", "")
				dx = {
					'key_value':key_value
				}
				try:
					bolsista = Bolsista.objects.get(cartao_rfid=key_value)
					acesso = Acesso.objects.filter(bolsista=bolsista).order_by('-id').first()
					if acesso is not None:

						if acesso.hora_saida == None:
							if acesso.data == date.today():
								
								acesso.hora_saida = timezone.localtime(timezone.now()).time()
								data_saida = date.today()
								acesso.total_horas = timedelta(hours = acesso.hora_saida.hour, minutes=acesso.hora_saida.minute, seconds=acesso.hora_saida.second, microseconds=1) - timedelta(hours = acesso.hora_entrada.hour, minutes=acesso.hora_entrada.minute, seconds=acesso.hora_entrada.second, microseconds=1)
								acesso.save()
								message = "Saída registrada %s"%bolsista.nome
								tag = "success"
								return HttpResponse(json.dumps({'message':message, 'tag':tag}), content_type='application/json')
							else:
								acesso.delete()
								novo_acesso = Acesso()
								novo_acesso.bolsista =  bolsista
								novo_acesso.data = date.today()
								novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
								novo_acesso.save()
								message = "Data fora do ultimo registro da data de entrada. Novo acesso gerado!"
								tag = "warning"
								return HttpResponse(json.dumps({'tag':tag,'message':message}), content_type='application/json')


						else:
							novo_acesso = Acesso()
							novo_acesso.bolsista =  bolsista
							novo_acesso.data = date.today()
							novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
							novo_acesso.save()
							message = "Entrada Registrada %s"%bolsista.nome
							tag = "success"
							return HttpResponse(json.dumps({'tag':tag,'message':message}), content_type='application/json')
					else:
						novo_acesso = Acesso()
						novo_acesso.bolsista =  bolsista
						novo_acesso.data = date.today()
						novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
						novo_acesso.save()
						
						message = "Entrada Registrada %s"%bolsista.nome
						return HttpResponse(json.dumps({'tag':tag,'message':message}), content_type='application/json')
				except Bolsista.DoesNotExist:
					op = '3'
					message = "Cartão não está relacionado a nenhum bolsista"
					tag = "notice"
					#messages.warning(request, 'Cartão não está relacionado a nenhum bolsista')
					return HttpResponse(json.dumps({'tag':tag,'message':message, 'key_value':key_value}), content_type='application/json')
		#return render(request, 'teste.html', {'key_value':key_value})
	except serial.SerialException as e:
		return render(request, 'teste.html', {'key_value':e})
	finally:
		con_serial.close()
