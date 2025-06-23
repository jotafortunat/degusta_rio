from django.db import models
from django.db.models import Avg, F

class Usuario(models.Model):
    id_user = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha_hash = models.CharField(max_length=255)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome
    
class AvaliacaoRestaurante(models.Model):
    ESTRELAS_CHOICES = [
        (1, '1 Estrela'),
        (2, '2 Estrelas'),
        (3, '3 Estrelas'),
        (4, '4 Estrelas'),
        (5, '5 Estrelas'),
    ]
    
    restaurante = models.ForeignKey('Restaurante', on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estrelas = models.PositiveSmallIntegerField(choices=ESTRELAS_CHOICES)
    comentario = models.TextField(max_length=500, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('restaurante', 'usuario')  # Cada usuário só pode avaliar 1 vez
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def __str__(self):
        return f"{self.usuario}: {self.estrelas} estrelas para {self.restaurante}"

class Restaurante(models.Model):
    id_restaurante = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200, blank=True)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to='fotos_restaurante/', null=True, blank=True)  # campo para foto
    descricao = models.TextField()
    avaliacao = models.FloatField(null=True, blank=True)
    
    PRECO_OPCOES = [
        ('$', '$ - Econômico'),
        ('$$', '$$ - Moderado'),
        ('$$$', '$$$ - Caro'),
    ]
    
    preco = models.CharField(
        max_length=3,
        choices=PRECO_OPCOES,
        default='$$',  # Opção padrão
        verbose_name='Faixa de Preço'
    )
    
    @property
    def media_avaliacoes(self):
        """Calcula a média entre a avaliação original e as avaliações dos usuários"""
        media_avaliacoes = self.avaliacoes.aggregate(media=Avg('estrelas'))['media'] or 0
        
        # Se houver avaliação original, calcula a média entre ela e as avaliações dos usuários
        if self.avaliacao and self.avaliacao > 0:
            return (self.avaliacao + media_avaliacoes) / 2
        return media_avaliacoes
    
    @media_avaliacoes.setter
    def media_avaliacoes(self, value):
        self._media_avaliacoes = value

    @property
    def total_avaliacoes(self):
        """Retorna o total de avaliações (incluindo comentários)"""
        return self.avaliacoes.count()

    def atualizar_media(self):
        """Atualiza o campo avaliacao com a média calculada"""
        self.avaliacao = self.media_avaliacoes
        self.save()

    def __str__(self):
        return self.nome
    
    @total_avaliacoes.setter
    def total_avaliacoes(self, value):
        self._total_avaliacoes = value
    
    
    @property
    def avaliacao_usuario(self, user):
        """Retorna a avaliação do usuário atual se existir"""
        if hasattr(self, '_avaliacao_usuario'):
            return self._avaliacao_usuario
        
        try:
            self._avaliacao_usuario = self.avaliacoes.get(usuario=user.usuario)
        except AvaliacaoRestaurante.DoesNotExist:
            self._avaliacao_usuario = None
        
        return self._avaliacao_usuario
    
    @avaliacao_usuario.setter
    def avaliacao_usuario(self, value):
        self._avaliacao_usuario = value