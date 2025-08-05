# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, MedicoProfile, PacienteProfile, EnfermeraProfile

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = [
        'email', 'cedula', 'first_name', 'last_name', 
        'tipo_usuario', 'edad', 'is_active'
    ]
    list_filter = [
        'tipo_usuario', 'is_active', 'genero', 'creado_en'
    ]
    search_fields = [
        'email', 'username', 'first_name', 'last_name', 'cedula'
    ]
    readonly_fields = ['edad', 'date_joined', 'creado_en', 'actualizado_en']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'cedula', 'telefono',
                'fecha_nacimiento', 'edad', 'direccion', 'genero'
            )
        }),
        ('Tipo de Usuario', {
            'fields': ('tipo_usuario',)
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('date_joined', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'tipo_usuario',
                'first_name', 'last_name', 'cedula', 'telefono', 'fecha_nacimiento'
            ),
        }),
    )
    
    def edad(self, obj):
        return obj.edad
    edad.short_description = 'Edad'

@admin.register(MedicoProfile)
class MedicoProfileAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_licencia', 'especializacion', 'anos_experiencia']
    list_filter = ['especializacion', 'anos_experiencia']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'numero_licencia']

@admin.register(PacienteProfile)
class PacienteProfileAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'grupo_sanguineo']
    list_filter = ['grupo_sanguineo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'numero_seguro']

@admin.register(EnfermeraProfile)
class EnfermeraProfileAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_registro']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'numero_registro']