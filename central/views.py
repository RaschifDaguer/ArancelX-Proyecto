from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from arancel.models import Seccion, Capitulo, Partida, Subpartida
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .models import HistorialBusqueda, Rol, PerfilUsuario
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import permission_required

def es_superusuario_o_tiene_permiso_usuarios(user):
    return user.is_superuser or (hasattr(user, 'perfil') and user.perfil.rol and user.perfil.rol.permisos_usuarios)

@login_required
def home(request):
    total_secciones = Seccion.objects.count()
    total_capitulos = Capitulo.objects.count()
    total_partidas = Partida.objects.count()
    total_subpartidas = Subpartida.objects.count()
    
    # Obtener historial de búsquedas del usuario (últimas 10)
    historial = HistorialBusqueda.objects.filter(usuario=request.user)[:10]
    
    return render(request, 'home.html', {
        'total_secciones': total_secciones,
        'total_capitulos': total_capitulos,
        'total_partidas': total_partidas,
        'total_subpartidas': total_subpartidas,
        'historial_busquedas': historial,
    })

@login_required
def limpiar_historial(request):
    if request.method == 'POST':
        HistorialBusqueda.objects.filter(usuario=request.user).delete()
        messages.success(request, 'Historial de búsquedas limpiado correctamente.')
    return redirect('home')

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def gestionar_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    roles = Rol.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol_id = request.POST.get('rol_id')
        accion = request.POST.get('accion')
        
        if accion == 'asignar_rol':
            usuario = get_object_or_404(User, id=usuario_id)
            rol = get_object_or_404(Rol, id=rol_id) if rol_id else None
            
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
            perfil.rol = rol
            perfil.save()
            
            messages.success(request, f'Rol "{rol.nombre if rol else "Sin rol"}" asignado a {usuario.username}')
            
        elif accion == 'activar_desactivar':
            usuario = get_object_or_404(User, id=usuario_id)
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
            perfil.activo = not perfil.activo
            perfil.save()
            
            estado = "activado" if perfil.activo else "desactivado"
            messages.success(request, f'Usuario {usuario.username} {estado}')
        elif accion == 'eliminar_usuario':
            usuario = get_object_or_404(User, id=usuario_id)
            if usuario.is_superuser:
                messages.error(request, 'No puedes eliminar un superusuario desde esta interfaz.')
            else:
                usuario.delete()
                messages.success(request, f'Usuario {usuario.username} eliminado correctamente.')
    
    return render(request, 'central/gestionar_usuarios.html', {
        'usuarios': usuarios,
        'roles': roles,
    })

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def gestionar_roles(request):
    roles = Rol.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'crear_rol':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            permisos_arancel = request.POST.get('permisos_arancel') == 'on'
            permisos_admin = request.POST.get('permisos_admin') == 'on'
            permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
            
            if nombre:
                # Verificar que no se duplique un rol del sistema
                if nombre.lower() in ['administrador', 'despachador de aduana']:
                    messages.error(request, f'El rol "{nombre}" ya existe en el sistema.')
                else:
                    rol = Rol.objects.create(
                        nombre=nombre,
                        descripcion=descripcion,
                        permisos_arancel=permisos_arancel,
                        permisos_admin=permisos_admin,
                        permisos_usuarios=permisos_usuarios
                    )
                    messages.success(request, f'Rol "{rol.nombre}" creado exitosamente')
            else:
                messages.error(request, 'El nombre del rol es obligatorio')
                
        elif accion == 'editar_rol':
            rol_id = request.POST.get('rol_id')
            rol = get_object_or_404(Rol, id=rol_id)
            
            # Permitir editar descripción y permisos de roles del sistema, pero no el nombre
            if rol.nombre in ['Administrador', 'Despachador de Aduana']:
                rol.descripcion = request.POST.get('descripcion', rol.descripcion)
                rol.permisos_arancel = request.POST.get('permisos_arancel') == 'on'
                rol.permisos_admin = request.POST.get('permisos_admin') == 'on'
                rol.permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
                rol.save()
                messages.success(request, f'Permisos del rol "{rol.nombre}" actualizados exitosamente')
            else:
                # Para roles personalizados, permitir editar todo
                rol.nombre = request.POST.get('nombre', rol.nombre)
                rol.descripcion = request.POST.get('descripcion', rol.descripcion)
                rol.permisos_arancel = request.POST.get('permisos_arancel') == 'on'
                rol.permisos_admin = request.POST.get('permisos_admin') == 'on'
                rol.permisos_usuarios = request.POST.get('permisos_usuarios') == 'on'
                rol.save()
                messages.success(request, f'Rol "{rol.nombre}" actualizado exitosamente')
            
        elif accion == 'eliminar_rol':
            rol_id = request.POST.get('rol_id')
            rol = get_object_or_404(Rol, id=rol_id)
            
            # Proteger roles del sistema
            if rol.nombre in ['Administrador', 'Despachador de Aduana']:
                messages.error(request, f'No se puede eliminar el rol "{rol.nombre}" porque es un rol del sistema.')
            else:
                # Verificar si hay usuarios usando este rol
                usuarios_con_rol = PerfilUsuario.objects.filter(rol=rol).count()
                if usuarios_con_rol > 0:
                    messages.error(request, f'No se puede eliminar el rol "{rol.nombre}" porque {usuarios_con_rol} usuario(s) lo están usando')
                else:
                    rol.delete()
                    messages.success(request, f'Rol "{rol.nombre}" eliminado exitosamente')
    
    return render(request, 'central/gestionar_roles.html', {
        'roles': roles,
    })

def register_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil de usuario por defecto
            PerfilUsuario.objects.create(usuario=user)
            messages.success(request, 'Usuario registrado correctamente. Ahora puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el registro. Por favor, verifica los datos.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si el usuario está activo
            try:
                perfil = user.perfil
                if not perfil.activo:
                    messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
                    return render(request, 'registration/login.html')
            except PerfilUsuario.DoesNotExist:
                # Si no tiene perfil, crear uno por defecto
                PerfilUsuario.objects.create(usuario=user)
            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request) 
    return redirect('login')    

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})    

@login_required
@user_passes_test(es_superusuario_o_tiene_permiso_usuarios)
def panel_admin_simplificado(request):
    """Panel de administración simplificado para usuarios con permisos de admin"""
    # Obtener estadísticas
    total_usuarios = User.objects.count()
    usuarios_activos = PerfilUsuario.objects.filter(activo=True).count()
    total_roles = Rol.objects.count()
    total_busquedas = HistorialBusqueda.objects.count()
    
    return render(request, 'central/panel_admin_simplificado.html', {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_roles': total_roles,
        'total_busquedas': total_busquedas,
    })

@login_required
def admin_redirect(request):
    """Redirige a usuarios según sus permisos"""
    if request.user.is_superuser:
        # Superusuarios van al admin completo
        return redirect('/admin/')
    elif hasattr(request.user, 'perfil') and request.user.perfil.rol and request.user.perfil.rol.permisos_admin:
        # Usuarios con permisos admin van al panel simplificado
        return redirect('panel_admin_simplificado')
    else:
        # Usuarios sin permisos van al home
        messages.warning(request, 'No tienes permisos para acceder al panel de administración.')
        return redirect('home')    