from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import TiposExames, SolicitacaoExame, PedidosExames, AcessoMedico
from datetime import datetime
from django.contrib.messages import constants
from django.contrib import messages

@login_required(login_url='/usuarios/login')
def solicitar_exames(request):
    if request.method == "GET":
        tipos_exames = TiposExames.objects.all()

        return render(request, 'index.html',{'tipos_exames':tipos_exames})
    
    if request.method =="POST":
        tipos_exames = TiposExames.objects.all()
        exame_id = request.POST.getlist("exames")
        solicitacao_exames = TiposExames.objects.filter(id__in = exame_id)
        preco_total = 0
        for i in solicitacao_exames:
            if i.disponivel:
                preco_total += i.preco
        return render(request, 'index.html',{'solicitacao_exames':solicitacao_exames,'tipos_exames':tipos_exames,'preco_total':preco_total})
    
@login_required(login_url='/usuarios/login')
def fechar_pedido(request):
    exames = request.POST.getlist('exames')
    solicitacao_exames = TiposExames.objects.filter(id__in = exames)

    pedido_exame = PedidosExames(
        usuario = request.user,
        data = datetime.now()
    )
    pedido_exame.save()
    for i in solicitacao_exames:
        solicitacao_exames_temp = SolicitacaoExame(usuario = request.user,
                                                   exame = i,
                                                   status = "E")
        solicitacao_exames_temp.save()
        pedido_exame.exames.add(solicitacao_exames_temp)
    pedido_exame.save()
    messages.add_message(request,constants.SUCCESS,"Exame solicitado com sucesso!")
    return redirect('/exames/gerenciar_pedidos')

@login_required(login_url='/usuarios/login')
def gerenciar_pedidos(request):
    if request.method =="GET":
        pedidos_exames = PedidosExames.objects.filter(usuario = request.user)


        return render(request,'gerenciar_pedidos.html',{'pedidos_exames':pedidos_exames})


@login_required(login_url='/usuarios/login')
def cancelar_pedido(request,pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)

    if not pedido.usuario == request.user:
        return redirect('/exames/gerenciar_pedidos')

    pedido.agendado = False
    pedido.save()
    messages.add_message(request,constants.SUCCESS,"Pedido cancelado com sucesso")
    return redirect('/exames/gerenciar_pedidos')

@login_required(login_url='/usuarios/login')
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario = request.user)
    print (exames)
    return render(request,'gerenciar_exames.html',{'exames':exames})



@login_required(login_url='/usuarios/login')
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if exame.resultado:
        if not exame.requer_senha:
            return redirect(exame.resultado.url)
        
        return redirect(f'/exames/solicitar_senha_exame/{exame_id}')
    else:
        messages.add_message(request,constants.ERROR,"Resultado ainda não foi publicado.")
        return redirect('/exames/gerenciar_exames/')

@login_required(login_url='/usuarios/login')
def solicitar_senha_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if request.method =="GET":
        return render(request,'solicitar_senha_exame.html',{'exame':exame})
    
    elif request.method =="POST":
        senha = request.POST.get('senha')
        if senha == exame.senha:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request,constants.ERROR,"Senha inválida")
            return redirect(f'/exames/solicitar_senha_exame/{exame.id}')


@login_required(login_url='/usuarios/login')
def gerar_acesso_medico(request):
    if request.method == "GET":
        acessos_medicos = AcessoMedico.objects.filter(usuario = request.user)
        return render(request,'gerar_acesso_medico.html', {'acessos_medicos':acessos_medicos})
    
    elif request.method == "POST":
        identificacao = request.POST.get('identificacao')
        tempo_de_acesso = request.POST.get('tempo_de_acesso')
        data_exame_inicial = request.POST.get("data_exame_inicial")
        data_exame_final = request.POST.get("data_exame_final")

        acesso_medico = AcessoMedico(
            usuario = request.user,
            identificacao = identificacao,
            tempo_de_acesso = tempo_de_acesso,
            data_exames_iniciais = data_exame_inicial,
            data_exames_finais = data_exame_final,
            criado_em = datetime.now()
        )

        acesso_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Acesso gerado com sucesso')
        return redirect('/exames/gerar_acesso_medico')


def acesso_medico (request, token):
    acesso_medico = AcessoMedico.objects.get(token=token)
    if acesso_medico.status =="Expirado":
        messages.add_message(request, constants.ERROR, 'Esse token já expirou, solicite outro')
        return redirect('/usuarios/login')
    
    pedidos = PedidosExames.objects.filter(usuario = acesso_medico.usuario).filter(data__gte = acesso_medico.data_exames_iniciais).filter(data__lte = acesso_medico.data_exames_finais)
    return render(request, 'acesso_medico.html', {'pedidos':pedidos})