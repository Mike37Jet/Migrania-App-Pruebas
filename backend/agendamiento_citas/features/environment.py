import os
import sys
import django


def before_all(context):
    """
    Configurar Django antes de ejecutar los tests
    """
    # Añadir el directorio del proyecto al path si no está
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Configurar la variable de entorno DJANGO_SETTINGS_MODULE
    # IMPORTANTE: Cambia 'migrania_app.settings' por el nombre correcto de tu módulo de settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migraine_app.settings')  # o el nombre correcto

    # Configurar Django
    django.setup()