from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.messages import constants


def cadastro(request):
    if request.method == "GET":
        return render(request,'cadastro/index.html')
    
    if request.method =="POST":
        primeiro_nome = request.POST.get('primeiro_nome')
        ultimo_nome = request.POST.get('ultimo_nome')
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not senha == confirmar_senha:
            messages.add_message(request,constants.INFO,'As senhas não coincidem.')
            return redirect('/usuarios/cadastro')
        
        valida_email = User.objects.filter(email=email).filter(username = username).exists()
        if valida_email:
            messages.add_message(request,constants.INFO,'Email ou username já existente.')
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            messages.add_message(request,constants.INFO,'A sua senha deve conter no mínimo 6 caracteres.')
            return redirect('/usuarios/cadastro')
        try:
            usuarios = User.objects.create_user(first_name=primeiro_nome, last_name=ultimo_nome,username=username,password = senha, email=email)
            messages.add_message(request,constants.SUCCESS,'Usuario cadastrado com sucesso!')
            return redirect('/usuarios/cadastro')
        
        except:
            messages.add_message(request,constants.ERROR,'Erro interno do sistema.')
            return redirect('/usuarios/cadastro')
        



def login(request):
    if request.method == "GET":
        return render(request,'login/index.html')
    
    if request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("senha")
        usuarios = auth.authenticate(username=username, password = senha)
        if usuarios:
            request.session['logado'] = True
            auth.login(request,usuarios)
            return redirect('/exames/solicitar_exames')
        else:
            messages.add_message(request,constants.ERROR,'Credenciais inválidas.')
            return redirect('/usuarios/login')

            
