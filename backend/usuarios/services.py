# usuarios/services.py
from typing import Dict, Any
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .repositories import AbstractUserRepository, DjangoUserRepository
from .models import Usuario, MedicoProfile, PacienteProfile, EnfermeraProfile


class UsuarioService:
    """Servicio para manejar la lógica de negocio de usuarios"""
    
    def __init__(self, repository: AbstractUserRepository = None):
        self.repository = repository or DjangoUserRepository()
    
    def obtener_todos_usuarios(self):
        """Obtener todos los usuarios activos"""
        return self.repository.get_all_users()
    
    def obtener_usuario_por_id(self, user_id: int):
        """Obtener usuario por ID"""
        return self.repository.get_user_by_id(user_id)
    
    def obtener_usuario_por_email(self, email: str):
        """Obtener usuario por email"""
        return self.repository.get_user_by_email(email)
    
    def obtener_usuario_por_cedula(self, cedula: str):
        """Obtener usuario por cédula"""
        return self.repository.get_user_by_cedula(cedula)
    
    def validar_datos_usuario_base(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Validar datos básicos de usuario y retornar errores si los hay"""
        errores = {}
        
        # Validar email único
        if 'email' in user_data:
            email = user_data['email']
            if self.repository.get_user_by_email(email):
                errores['email'] = 'Este email ya está registrado'
        
        # Validar cédula única
        if 'cedula' in user_data:
            cedula = user_data['cedula']
            if len(cedula) != 10:
                errores['cedula'] = 'La cédula debe tener exactamente 10 dígitos'
            elif not cedula.isdigit():
                errores['cedula'] = 'La cédula debe contener solo números'
            elif self.repository.get_user_by_cedula(cedula):
                errores['cedula'] = 'Esta cédula ya está registrada'
        
        # Validar teléfono
        if 'telefono' in user_data:
            telefono = user_data['telefono']
            if len(telefono) != 10:
                errores['telefono'] = 'El teléfono debe tener exactamente 10 dígitos'
            elif not telefono.isdigit():
                errores['telefono'] = 'El teléfono debe contener solo números'
        
        return errores
    
    def crear_medico(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]):
        """Crear médico con validaciones de negocio"""
        try:
            # Validar datos base del usuario
            errores = self.validar_datos_usuario_base(user_data)
            if errores:
                raise ValidationError(errores)
            
            # Validar datos específicos del médico
            errores_medico = self._validar_datos_medico(profile_data)
            if errores_medico:
                raise ValidationError(errores_medico)
            
            # Crear el médico
            usuario = self.repository.create_medico(user_data, profile_data)
            return usuario
            
        except IntegrityError as e:
            if 'numero_licencia' in str(e).lower():
                raise ValidationError({'numero_licencia': 'Este número de licencia ya está registrado'})
            raise ValidationError({'error': 'Error de integridad en los datos'})
    
    def crear_paciente(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]):
        """Crear paciente con validaciones de negocio"""
        try:
            # Validar datos base del usuario
            errores = self.validar_datos_usuario_base(user_data)
            if errores:
                raise ValidationError(errores)
            
            # Validar datos específicos del paciente
            errores_paciente = self._validar_datos_paciente(profile_data)
            if errores_paciente:
                raise ValidationError(errores_paciente)
            
            # Crear el paciente
            usuario = self.repository.create_paciente(user_data, profile_data)
            return usuario
            
        except IntegrityError:
            raise ValidationError({'error': 'Error de integridad en los datos'})
    
    def crear_enfermera(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]):
        """Crear enfermera con validaciones de negocio"""
        try:
            # Validar datos base del usuario
            errores = self.validar_datos_usuario_base(user_data)
            if errores:
                raise ValidationError(errores)
            
            # Validar datos específicos de la enfermera
            errores_enfermera = self._validar_datos_enfermera(profile_data)
            if errores_enfermera:
                raise ValidationError(errores_enfermera)
            
            # Crear la enfermera
            usuario = self.repository.create_enfermera(user_data, profile_data)
            return usuario
            
        except IntegrityError as e:
            if 'numero_registro' in str(e).lower():
                raise ValidationError({'numero_registro': 'Este número de registro ya está registrado'})
            raise ValidationError({'error': 'Error de integridad en los datos'})
    
    def obtener_todos_medicos(self):
        """Obtener todos los médicos activos"""
        return self.repository.get_all_medicos()
    
    def obtener_todos_pacientes(self):
        """Obtener todos los pacientes activos"""
        return self.repository.get_all_pacientes()
    
    def obtener_todas_enfermeras(self):
        """Obtener todas las enfermeras activas"""
        return self.repository.get_all_enfermeras()
    
    def obtener_medico_por_licencia(self, numero_licencia: str):
        """Obtener médico por número de licencia"""
        return self.repository.get_medico_by_license(numero_licencia)
    
    def obtener_enfermera_por_registro(self, numero_registro: str):
        """Obtener enfermera por número de registro"""
        return self.repository.get_enfermera_by_registro(numero_registro)
    
    def actualizar_usuario(self, user_id: int, data: Dict[str, Any]):
        """Actualizar datos de usuario"""
        # Validar datos si se están actualizando
        errores = {}
        
        if 'telefono' in data:
            telefono = data['telefono']
            if len(telefono) != 10 or not telefono.isdigit():
                errores['telefono'] = 'El teléfono debe tener exactamente 10 dígitos numéricos'
        
        if errores:
            raise ValidationError(errores)
        
        return self.repository.update_usuario(user_id, data)
    
    def desactivar_usuario(self, user_id: int) -> bool:
        """Desactivar usuario (soft delete)"""
        return self.repository.deactivate_usuario(user_id)
    
    def generar_dashboard_datos(self, usuario):
        """Generar datos del dashboard según el tipo de usuario"""
        base_data = {
            'usuario': {
                'id': usuario.id,
                'nombre_completo': usuario.get_full_name(),
                'email': usuario.email,
                'tipo_usuario': usuario.tipo_usuario,
            }
        }
        
        if usuario.es_medico:
            perfil = getattr(usuario, 'perfil_medico', None)
            base_data.update({
                'tipo_usuario': 'medico',
                'especializacion': perfil.especializacion if perfil else None,
                'numero_licencia': perfil.numero_licencia if perfil else None,
                'permisos': {
                    'puede_ver_todos_pacientes': True,
                    'puede_crear_diagnosticos': True,
                    'puede_prescribir_tratamientos': True,
                    'puede_agendar_citas': True,
                }
            })
        
        elif usuario.es_enfermera:
            perfil = getattr(usuario, 'perfil_enfermera', None)
            base_data.update({
                'tipo_usuario': 'enfermera',
                'departamento': perfil.departamento if perfil else None,
                'permisos': {
                    'puede_ver_pacientes_asignados': True,
                    'puede_registrar_vitales': True,
                    'puede_administrar_medicamentos': True,
                    'puede_agendar_citas': True,
                }
            })
        
        else:  # paciente
            perfil = getattr(usuario, 'perfil_paciente', None)
            base_data.update({
                'tipo_usuario': 'paciente',
                'grupo_sanguineo': perfil.grupo_sanguineo if perfil else None,
                'permisos': {
                    'puede_agendar_citas': True,
                    'puede_ver_historial_propio': True,
                    'puede_completar_evaluaciones': True,
                    'puede_registrar_episodios': True,
                }
            })
        
        return base_data
    
    def obtener_lista_medicos_resumida(self):
        """Obtener lista resumida de médicos para APIs"""
        medicos = self.repository.get_all_medicos()
        
        data = []
        for medico in medicos:
            data.append({
                'id': medico.usuario.id,
                'nombre_completo': medico.usuario.get_full_name(),
                'email': medico.usuario.email,
                'especializacion': medico.get_especializacion_display(),
                'numero_licencia': medico.numero_licencia,
                'anos_experiencia': medico.anos_experiencia,
            })
        
        return {'medicos': data, 'count': len(data)}
    
    def obtener_lista_pacientes_resumida(self):
        """Obtener lista resumida de pacientes para APIs"""
        pacientes = self.repository.get_all_pacientes()
        
        data = []
        for paciente in pacientes:
            data.append({
                'id': paciente.usuario.id,
                'nombre_completo': paciente.usuario.get_full_name(),
                'email': paciente.usuario.email,
                'grupo_sanguineo': paciente.grupo_sanguineo,
                'contacto_emergencia': paciente.contacto_emergencia_nombre,
                'telefono_emergencia': paciente.contacto_emergencia_telefono,
            })
        
        return {'pacientes': data, 'count': len(data)}
    
    def obtener_lista_enfermeras_resumida(self):
        """Obtener lista resumida de enfermeras para APIs"""
        enfermeras = self.repository.get_all_enfermeras()
        
        data = []
        for enfermera in enfermeras:
            data.append({
                'id': enfermera.usuario.id,
                'nombre_completo': enfermera.usuario.get_full_name(),
                'email': enfermera.usuario.email,
                'numero_registro': enfermera.numero_registro,
                'departamento': enfermera.departamento,
            })
        
        return {'enfermeras': data, 'count': len(data)}
    
    # Métodos privados de validación
    def _validar_datos_medico(self, profile_data: Dict[str, Any]) -> Dict[str, str]:
        """Validar datos específicos del médico"""
        errores = {}
        
        # Validar número de licencia único
        if 'numero_licencia' in profile_data:
            numero_licencia = profile_data['numero_licencia']
            if self.repository.get_medico_by_license(numero_licencia):
                errores['numero_licencia'] = 'Este número de licencia ya está registrado'
        
        # Validar años de experiencia
        if 'anos_experiencia' in profile_data:
            anos = profile_data['anos_experiencia']
            if not isinstance(anos, int) or anos < 0:
                errores['anos_experiencia'] = 'Los años de experiencia deben ser un número positivo'
            elif anos > 50:
                errores['anos_experiencia'] = 'Los años de experiencia no pueden ser mayores a 50'
        
        return errores
    
    def _validar_datos_paciente(self, profile_data: Dict[str, Any]) -> Dict[str, str]:
        """Validar datos específicos del paciente"""
        errores = {}
        
        # Validar teléfono de contacto de emergencia
        if 'contacto_emergencia_telefono' in profile_data:
            telefono = profile_data['contacto_emergencia_telefono']
            if len(telefono) < 7 or len(telefono) > 15:
                errores['contacto_emergencia_telefono'] = 'El teléfono de emergencia debe tener entre 7 y 15 dígitos'
        
        return errores
    
    def _validar_datos_enfermera(self, profile_data: Dict[str, Any]) -> Dict[str, str]:
        """Validar datos específicos de la enfermera"""
        errores = {}
        
        # Validar número de registro único
        if 'numero_registro' in profile_data:
            numero_registro = profile_data['numero_registro']
            if self.repository.get_enfermera_by_registro(numero_registro):
                errores['numero_registro'] = 'Este número de registro ya está registrado'
        
        return errores



# Instancia global del servicio para usar en viewsets y serializers
usuario_service = UsuarioService()
