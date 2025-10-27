from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos_arancel = models.BooleanField(default=False, help_text="Puede ver y buscar en aranceles")
    permisos_admin = models.BooleanField(default=False, help_text="Puede acceder al panel de administración")
    permisos_usuarios = models.BooleanField(default=False, help_text="Puede gestionar usuarios y roles")
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre if self.rol else 'Sin rol'}"

class HistorialBusqueda(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    fecha_busqueda = models.DateTimeField(auto_now_add=True)
    tipo_resultado = models.CharField(max_length=50, blank=True, null=True)  # Sección, Capítulo, Partida, Subpartida
    id_resultado = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_busqueda']
        verbose_name = 'Historial de Búsqueda'
        verbose_name_plural = 'Historiales de Búsqueda'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.termino_busqueda} ({self.fecha_busqueda.strftime('%d/%m/%Y %H:%M')})"
