import os
import sys
import django

def before_all(context):
    """Configurar Django antes de ejecutar todos los tests de Behave"""
    
    # Configurar Django - usar settings_ci si estamos en CI
    if os.getenv('CI') == 'true':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings_ci')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings')
    
    # Verificar si Django ya está configurado (evitar error "populate() isn't reentrant")
    from django.apps import apps
    
    if not apps.ready:
        try:
            django.setup()
        except RuntimeError as e:
            if "populate() isn't reentrant" not in str(e):
                raise
    
    # Verificación final
    if not apps.ready:
        raise Exception("Django apps no están configuradas correctamente")
