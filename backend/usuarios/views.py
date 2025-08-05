# usuarios/views.py 
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model

Usuario = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def opciones_formulario(request):
    """Opciones para formularios de registro"""
    return Response({
        'generos': [
            {'value': 'M', 'label': 'Masculino'},
            {'value': 'F', 'label': 'Femenino'},
            {'value': 'O', 'label': 'Otro'},
            {'value': 'N', 'label': 'Prefiero no decir'},
        ],
        'grupos_sanguineos': [
            {'value': 'A+', 'label': 'A+'},
            {'value': 'A-', 'label': 'A-'},
            {'value': 'B+', 'label': 'B+'},
            {'value': 'B-', 'label': 'B-'},
            {'value': 'AB+', 'label': 'AB+'},
            {'value': 'AB-', 'label': 'AB-'},
            {'value': 'O+', 'label': 'O+'},
            {'value': 'O-', 'label': 'O-'},
        ],
        'especializaciones_medicas': [
            {'value': 'neurologia', 'label': 'Neurología'},
            {'value': 'medicina_general', 'label': 'Medicina General'},
            {'value': 'medicina_interna', 'label': 'Medicina Interna'},
            {'value': 'psiquiatria', 'label': 'Psiquiatría'},
            {'value': 'neurocirugia', 'label': 'Neurocirugía'},
            {'value': 'otra', 'label': 'Otra'},
        ]
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validar_cedula(request):
    """ Validar disponibilidad de cédula"""
    cedula = request.data.get('cedula')
    if not cedula:
        return Response({'error': 'Cédula requerida'}, status=status.HTTP_400_BAD_REQUEST)
    
    existe = Usuario.objects.filter(cedula=cedula).exists()
    return Response({
        'cedula': cedula,
        'disponible': not existe,
        'mensaje': 'Cédula disponible' if not existe else 'Cédula ya registrada'
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validar_email(request):
    """ Validar disponibilidad de email"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    existe = Usuario.objects.filter(email=email).exists()
    return Response({
        'email': email,
        'disponible': not existe,
        'mensaje': 'Email disponible' if not existe else 'Email ya registrado'
    })