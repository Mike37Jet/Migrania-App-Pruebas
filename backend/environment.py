import os
import sys
import django
from django.test.utils import setup_test_environment

def before_all(context):
    """
    Configurar Django antes de ejecutar todos los tests de Behave
    Este environment.py sirve para TODAS las apps del proyecto
    """
    
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
            setup_test_environment()
        except RuntimeError as e:
            if "populate() isn't reentrant" not in str(e):
                print(f"Error setting up Django: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error setting up Django: {e}")
            # No relanzar el error para permitir que continúen las pruebas
    
    # Verificación final
    if not apps.ready:
        print("Warning: Django apps no están configuradas correctamente")
    else:
        print("Django configurado correctamente para Behave tests")

def after_all(context):
    """
    Limpiar después de todas las pruebas
    """
    try:
        from django.test.utils import teardown_test_environment
        teardown_test_environment()
    except:
        pass