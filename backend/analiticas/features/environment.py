import os
import django

def before_all(context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "migraine_app.settings")
    django.setup()