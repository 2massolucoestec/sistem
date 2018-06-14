from django.http import JsonResponse
import serial
import json
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .forms import OrientadorForm, BolsistaForm, AcessoForm
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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def registrar(request):
    
    # Se dados forem passados via POST
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid(): # se o formulario for valido
            form.save() # cria um novo usuario a partir dos dados enviados 
            return redirect("/login/") # redireciona para a tela de login
        else:
            # mostra novamente o formulario de cadastro com os erros do formulario atual
            return render(request, "registrar.html", {"form": form})
    
    # se nenhuma informacao for passada, exibe a pagina de cadastro com o formulario
    return render(request, "registrar.html", {"form": UserCreationForm() })



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
							acesso.hora_saida = timezone.localtime(timezone.now()).time()
							acesso.total_horas = timedelta(hours = acesso.hora_saida.hour, minutes=acesso.hora_saida.minute, seconds=acesso.hora_saida.second) - timedelta(hours = acesso.hora_entrada.hour, minutes=acesso.hora_entrada.minute, seconds=acesso.hora_entrada.second)
							acesso.save()
							message = "Saída registrada"
							return HttpResponse(json.dumps({'message':message}), content_type='application/json')
						else:
							novo_acesso = Acesso()
							novo_acesso.bolsista =  bolsista
							novo_acesso.data = date.today()
							novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
							novo_acesso.save()
							message = "Entrada Registrada"
							return HttpResponse(json.dumps({'message':message}), content_type='application/json')
					else:
						novo_acesso = Acesso()
						novo_acesso.bolsista =  bolsista
						novo_acesso.data = date.today()
						novo_acesso.hora_entrada = timezone.localtime(timezone.now()).time()
						novo_acesso.save()
						message = "Entrada Registrada"
						return HttpResponse(json.dumps({'message':message}), content_type='application/json')
				except Bolsista.DoesNotExist:
					message = "Cartão não está relacionado a nenhum bolsista"
					return HttpResponse(json.dumps({'message':message, 'key_value':key_value}), content_type='application/json')
		#return render(request, 'teste.html', {'key_value':key_value})
	except serial.SerialException as e:
		return render(request, 'teste.html', {'key_value':e})
	finally:
		con_serial.close()
