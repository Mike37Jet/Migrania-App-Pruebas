# usuarios/managers.py
from django.contrib.auth.models import BaseUserManager
from datetime import date


class UsuarioManager(BaseUserManager):
    """Manager personalizado para Usuario"""

    def _create_user(self, email, username, password, **extra_fields):
        """Crear y guardar un usuario con email, username y password"""
        if not email:
            raise ValueError("El Email es obligatorio")
        if not username:
            raise ValueError("El Username es obligatorio")

        email = self.normalize_email(email)

        # Campos por defecto si no se proporcionan
        if "fecha_nacimiento" not in extra_fields:
            extra_fields["fecha_nacimiento"] = date(1987, 1, 1)  # Fecha por defecto
        if "cedula" not in extra_fields:
            extra_fields["cedula"] = "0000000000"  # Cédula por defecto
        if "telefono" not in extra_fields:
            extra_fields["telefono"] = "0000000000"
        if "direccion" not in extra_fields:
            extra_fields["direccion"] = "Sin dirección"
        if "genero" not in extra_fields:
            extra_fields["genero"] = "N"  # Prefiero no decir
        if "tipo_usuario" not in extra_fields:
            extra_fields["tipo_usuario"] = "medico"

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        """Crear usuario normal"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Crear superusuario"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)
