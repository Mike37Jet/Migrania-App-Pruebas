from rest_framework import permissions


class EsPaciente(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios
    que son de tipo 'Paciente'.
    """
    message = "Solo los pacientes pueden realizar esta acción."

    def has_permission(self, request, view):
        # Primero, verificamos que el usuario esté autenticado y tenga un tipo de usuario.
        if not (request.user and request.user.is_authenticated):
            return False

        # Luego, verificamos si el tipo de usuario es PACIENTE.
        return request.user.es_paciente


class EsPropietarioDeLaAutoevaluacionOPersonalMedico(permissions.BasePermission):
    """
    Permiso a nivel de objeto para permitir el acceso a una autoevaluación MIDAS
    solo si el solicitante es el paciente propietario o si es personal médico
    (Médico o Enfermera).
    """
    message = "No tienes permiso para ver o modificar esta evaluación."

    def has_object_permission(self, request, view, obj):
        # Primero, verificamos que el usuario esté autenticado.
        if not (request.user and request.user.is_authenticated):
            return False

        # El personal médico (Médicos y Enfermeras) tiene permiso para ver cualquier episodio.
        if request.user.es_medico or request.user.es_enfermera:
            return True

        # Si el usuario es un paciente, verificamos si es el propietario de la autoevaluacion.
        if request.user.es_paciente:
            return obj.paciente == request.user

        # Si no cumple ninguna de las condiciones anteriores, no tiene permiso.
        return False

class EsPropietarioDelEpisodioOPersonalMedico(permissions.BasePermission):
    """
    Permiso a nivel de objeto para permitir el acceso a un episodio
    solo si el solicitante es el paciente propietario o si es personal médico
    (Médico o Enfermera).
    """
    message = "No tienes permiso para ver o modificar este episodio."

    def has_object_permission(self, request, view, obj):
        # Primero, verificamos que el usuario esté autenticado.
        if not (request.user and request.user.is_authenticated):
            return False

        # El personal médico (Médicos y Enfermeras) tiene permiso para ver cualquier episodio.
        if request.user.es_medico or request.user.es_enfermera:
            return True

        # Si el usuario es un paciente, verificamos si es el propietario del episodio.
        if request.user.es_paciente:
            return obj.paciente == request.user

        # Si no cumple ninguna de las condiciones anteriores, no tiene permiso.
        return False