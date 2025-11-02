from django import forms
from django.contrib.auth.models import User

class HistorialBusquedaFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    tipo_resultado = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('Sección', 'Sección'),
            ('Capítulo', 'Capítulo'),
            ('Partida', 'Partida'),
            ('Subpartida', 'Subpartida'),
            ('Sin resultado', 'Sin resultado'),
            ('Resultados múltiples', 'Resultados múltiples'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    palabra_clave = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar término...'})
    )

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        strip=False,
        help_text='',
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    confirm_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        strip=False,
        help_text='',
        error_messages={'required': 'Por favor, confirma la contraseña.'}
    )

    class Meta:
        model = User
        fields = ('username',)
        labels = {
            'username': 'Nombre de usuario',
        }
        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio.',
                'unique': 'Este nombre de usuario ya está en uso.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user 