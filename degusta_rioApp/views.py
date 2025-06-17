from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsuarioForm, AvaliacaoForm
from django.contrib import messages
from .models import Usuario, Restaurante, AvaliacaoRestaurante
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Avg, Count, F, Q



def cadastro_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # ou qualquer outra página após cadastro
    else:
        form = UsuarioForm()
    return render(request, 'cadastro.html', {'form': form})



def login_usuario(request):
    if request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(senha, usuario.senha_hash):
                request.session['usuario_id'] = usuario.id_user
                request.session['usuario_nome'] = usuario.nome
                return redirect('adicionar_restaurante')
            else:
                erro = "Senha incorreta"
        except Usuario.DoesNotExist:
            erro = "Usuário não encontrado"

        return render(request, 'login.html', {'erro': erro})

    return render(request, 'login.html')




def pagina_inicial(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    # Aqui você pode buscar dados para mostrar na página inicial
    return render(request, 'pagina_inicial.html')


def logout_usuario(request):
    try:
        del request.session['usuario_id']
    except KeyError:
        pass
    return redirect('pagina_restaurantes')


from django.db.models import Q, F, Avg
from django.shortcuts import render
from .models import Restaurante  # Certifique-se de importar seu modelo Restaurante

def pagina_restaurantes(request):
    search_query = request.GET.get('q', '')
    
    # Verifica se o usuário está logado
    usuario_logado = 'usuario_id' in request.session
    usuario_id = request.session.get('usuario_id')

    # Obtém os restaurantes com as médias calculadas
    restaurantes = Restaurante.objects.annotate(
        media_usuarios=Coalesce(Avg('avaliacoes__estrelas'), 0.0),
        total_avaliacoes=Count('avaliacoes')
    ).annotate(
        media_final=(F('avaliacao') * 0.4) + (F('media_usuarios') * 0.6)
    )
    
    # Filtra por pesquisa se houver termo
    if search_query:
        restaurantes = restaurantes.filter(
            Q(nome__icontains=search_query) | 
            Q(descricao__icontains=search_query) |
            Q(endereco__icontains=search_query)
        )
    
    # Ordenação principal por média final (decrescente) e secundária por nome
    restaurantes = restaurantes.order_by(
        '-media_final',  # Maiores médias primeiro
        'nome'          # Em caso de empate, ordena por nome
    )
    
    # Pré-busca as avaliações do usuário logado (se existir)
    avaliacoes_usuario = {}
    if usuario_logado and usuario_id:
        avaliacoes = AvaliacaoRestaurante.objects.filter(
            usuario_id=usuario_id,
            restaurante__in=[r.id_restaurante for r in restaurantes]
        ).select_related('usuario')
        
        avaliacoes_usuario = {av.restaurante_id: av for av in avaliacoes}
    
    # Adiciona a avaliação do usuário como atributo dinâmico
    for restaurante in restaurantes:
        restaurante.usuario_avaliou = avaliacoes_usuario.get(restaurante.id_restaurante)
        # Adiciona os campos anotados como propriedades para fácil acesso no template
        restaurante.media_avaliacoes = restaurante.media_usuarios
        restaurante.total_avaliacoes = restaurante.total_avaliacoes
    
    context = {
        'restaurantes': restaurantes,
        'search_query': search_query,
        'usuario_logado': usuario_logado,
        'usuario_nome': request.session.get('usuario_nome', ''),
    }
    
    return render(request, 'restaurantes.html', context)

def adicionar_avaliacao(request, restaurante_id):
    # Verifica se o usuário está logado
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para avaliar')
        return redirect('login') + f'?next={request.path}'
    
    restaurante = get_object_or_404(Restaurante, id_restaurante=restaurante_id)
    usuario = get_object_or_404(Usuario, id_user=request.session['usuario_id'])
    
    # Verifica se já existe avaliação deste usuário
    avaliacao_existente = AvaliacaoRestaurante.objects.filter(
        restaurante=restaurante,
        usuario=usuario
    ).first()
    
    if request.method == 'POST':
        estrelas = request.POST.get('estrelas')
        comentario = request.POST.get('comentario', '')
        
        # Validação básica
        if not estrelas or not estrelas.isdigit() or int(estrelas) not in range(1, 6):
            messages.error(request, 'Avaliação inválida')
            return redirect('pagina_restaurantes')
        
        # Cria ou atualiza a avaliação
        if avaliacao_existente:
            avaliacao_existente.estrelas = estrelas
            avaliacao_existente.comentario = comentario
            avaliacao_existente.save()
            messages.success(request, 'Avaliação atualizada com sucesso!')
        else:
            AvaliacaoRestaurante.objects.create(
                restaurante=restaurante,
                usuario=usuario,
                estrelas=estrelas,
                comentario=comentario
            )
            messages.success(request, 'Avaliação registrada com sucesso!')
        
        # Atualiza a média do restaurante
        restaurante.atualizar_media()
        
        return redirect('pagina_restaurantes')
    
    return redirect('pagina_restaurantes')


def adicionar_restaurante(request):
    # Verificação do usuário na sessão
    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id_user=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

    if request.method == 'POST':
        # Criar o restaurante
        restaurante = Restaurante(
            nome=request.POST['nome'],
            endereco=request.POST['endereco'],
            descricao=request.POST['descricao'],
            foto=request.FILES.get('foto'),
            criado_por=usuario,  # Usa o usuário obtido da sessão
            preco=request.POST['preco'],
        )
        restaurante.save()
        
        # Criar a avaliação
        avaliacao = AvaliacaoRestaurante(
            restaurante=restaurante,
            usuario=usuario,
            estrelas=request.POST['estrelas'],
            comentario=request.POST.get('comentario', '')
        )
        avaliacao.save()
        
        
        return redirect('pagina_restaurantes')
    
    context = {
        'preco_opcoes': Restaurante.PRECO_OPCOES
    }
    
    return render(request, 'adicionar_restaurante.html', {'usuario_logado': usuario})


def perfil(request):
    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id_user=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

    restaurantes = Restaurante.objects.filter(criado_por=usuario)

    if request.method == 'POST':
        # Atualizar nome, email, senha
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if nome:
            usuario.nome = nome
        if email:
            usuario.email = email
        if senha:
            from django.contrib.auth.hashers import make_password
            usuario.senha_hash = make_password(senha)
        usuario.save()
        return redirect('perfil')

    return render(request, 'perfil.html', {'usuario': usuario, 'restaurantes': restaurantes})

@require_POST
def deletar_restaurante(request, restaurante_id):
    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id_user=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

    restaurante = get_object_or_404(Restaurante, id_restaurante=restaurante_id, criado_por=usuario)
    restaurante.delete()
    return redirect('perfil')


def deletar_avaliacao(request, avaliacao_id):
    # Verifica se o usuário está logado
    if 'usuario_id' not in request.session:
        messages.error(request, 'Você precisa fazer login para esta ação')
        return redirect('login')
    
    # Obtém a avaliação
    avaliacao = get_object_or_404(AvaliacaoRestaurante, id=avaliacao_id)
    usuario_id = request.session['usuario_id']
    
    # Verifica se o usuário é o dono da avaliação
    if avaliacao.usuario.id_user != usuario_id:
        messages.error(request, 'Você não tem permissão para apagar esta avaliação')
        return redirect('pagina_restaurantes')
    
    # Deleta a avaliação e atualiza a média
    restaurante = avaliacao.restaurante
    avaliacao.delete()
    restaurante.atualizar_media()
    
    messages.success(request, 'Avaliação removida com sucesso!')
    return redirect('pagina_restaurantes')