from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha')

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'data_nascimento']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.senha_hash = make_password(self.cleaned_data['senha'])
        if commit:
            usuario.save()
        return usuario


from django import forms
from .models import AvaliacaoRestaurante

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoRestaurante
        fields = ['estrelas', 'comentario']
        widgets = {
            'estrelas': forms.RadioSelect(choices=AvaliacaoRestaurante.ESTRELAS_CHOICES),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Deixe seu comentário (opcional)'}),
        }
        labels = {
            'estrelas': 'Sua avaliação',
            'comentario': 'Comentário'
        }