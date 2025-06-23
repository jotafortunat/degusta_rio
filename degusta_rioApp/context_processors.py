# seu_app/context_processors.py

from .models import Usuario

def usuario_logado(request):
    usuario = None
    if request.session.get('usuario_id'):
        try:
            usuario = Usuario.objects.get(id_user=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            pass
    return {'usuario_logado': usuario}
