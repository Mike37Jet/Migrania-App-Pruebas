# usuarios/permissions.py
from rest_framework import permissions

class EsMedico(permissions.BasePermission):
    """Solo médicos pueden acceder"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.es_medico

class EsPaciente(permissions.BasePermission):
    """Solo pacientes pueden acceder"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.es_paciente

class EsEnfermera(permissions.BasePermission):
    """Solo enfermeras pueden acceder"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.es_enfermera

class EsMedicoOEnfermera(permissions.BasePermission):
    """Solo médicos y enfermeras pueden acceder"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_medico or request.user.es_enfermera))

class EsPersonalMedico(permissions.BasePermission):
    """Solo médicos y enfermeras pueden escribir, todos pueden leer"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (request.user.is_authenticated and 
                (request.user.es_medico or request.user.es_enfermera))

class EsPropietarioOPersonalMedico(permissions.BasePermission):
    """Solo el propietario de los datos o personal médico puede acceder"""
    def has_object_permission(self, request, view, obj):
        # Si es personal médico, puede acceder a todo
        if request.user.es_medico or request.user.es_enfermera:
            return True
        
        # Si es paciente, solo puede acceder a sus propios datos
        if hasattr(obj, 'paciente'):
            return obj.paciente == request.user
        elif hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False