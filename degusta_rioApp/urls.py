from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    path('logout/', views.logout_usuario, name='logout'),
    path('', views.pagina_restaurantes, name='pagina_restaurantes'),
    path('restaurantes/adicionar/', views.adicionar_restaurante, name='adicionar_restaurante'),
    path('restaurante/deletar/<int:restaurante_id>/', views.deletar_restaurante, name='deletar_restaurante'),
    path('perfil/', views.perfil, name='perfil'),
    path('restaurantes/<int:restaurante_id>/avaliar/', views.adicionar_avaliacao, name='adicionar_avaliacao'),
    path('avaliacoes/<int:avaliacao_id>/deletar/', views.deletar_avaliacao, name='deletar_avaliacao'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)