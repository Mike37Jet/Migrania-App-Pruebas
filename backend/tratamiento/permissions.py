from rest_framework import permissions


class EsMedico(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios médicos.
    """
    message = "Solo los médicos pueden realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            user.tipo_usuario == 'medico' and
            hasattr(user, 'perfil_medico')
        )


class EsPaciente(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios pacientes.
    """
    message = "Solo los pacientes pueden realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, 'perfil_paciente')


class EsPropietarioDelTratamientoOPersonalMedico(permissions.BasePermission):
    """
    Permiso a nivel de objeto para permitir el acceso a un tratamiento
    solo si el solicitante es el paciente propietario o si es personal médico.
    """
    message = "No tienes permiso para ver o modificar este tratamiento."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # El personal médico tiene permiso para ver cualquier tratamiento
        if hasattr(user, 'perfil_medico'):
            return True

        # Si es paciente, verificar si es el propietario del tratamiento
        if hasattr(user, 'perfil_paciente'):
            return obj.paciente.usuario == user  # Nota el acceso a usuario aquí

        return False


class EsPropietarioDelMedicamentoOPersonalMedico(permissions.BasePermission):
    """
    Permiso a nivel de objeto para medicamentos basado en tratamientos.
    """
    message = "No tienes permiso para ver o modificar este medicamento."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # El personal médico puede ver cualquier medicamento
        if hasattr(user, 'perfil_medico'):
            return True

        # Si es paciente, verificar si el medicamento pertenece a sus tratamientos
        if hasattr(user, 'perfil_paciente'):
            return obj.tratamientos.filter(paciente__usuario=user).exists()

        return False


class PuedeConfirmarToma(permissions.BasePermission):
    """
    Permiso específico para confirmar tomas - Solo pacientes pueden confirmar sus tomas.
    """
    message = "Solo puedes confirmar tus propias tomas de medicamentos."

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, 'perfil_paciente')

    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(user, 'perfil_paciente'):
            return obj.paciente.usuario == user
        return False
