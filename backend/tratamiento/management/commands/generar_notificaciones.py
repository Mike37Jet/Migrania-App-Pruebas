from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from tratamiento.models import Tratamiento, Medicamento, Alerta, Recordatorio, EstadoNotificacion
from usuarios.models import PacienteProfile
from evaluacion_diagnostico.models import EpisodioCefalea

class Command(BaseCommand):
    help = 'Genera notificaciones de prueba para testing del frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tratamiento-id',
            type=int,
            help='ID específico del tratamiento a usar',
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar notificaciones existentes antes de crear nuevas',
        )
        parser.add_argument(
            '--sin-procesar',
            action='store_true',
            help='No procesar las notificaciones después de crearlas (solo para debugging)',
        )
        parser.add_argument(
            '--testing-rapido',
            action='store_true',
            help='Para testing rápido: recordatorio ahora, alerta en 1 minuto',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Generando notificaciones de prueba...')
        )

        try:
            # Obtener o crear tratamiento
            tratamiento = self.obtener_tratamiento(options.get('tratamiento_id'))
            if not tratamiento:
                return

            # Limpiar notificaciones existentes si se solicita
            if options.get('limpiar'):
                self.limpiar_notificaciones(tratamiento)

            # Crear notificaciones de prueba
            self.crear_notificaciones_prueba(tratamiento, options.get('testing_rapido', False))

            # Procesar notificaciones para activar las que correspondan por tiempo
            if not options.get('sin_procesar'):
                self.procesar_notificaciones(tratamiento)
            else:
                self.stdout.write('⏭️ Omitiendo procesamiento (solo para debugging)')

            # Mostrar resumen
            self.mostrar_resumen(tratamiento)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )

    def obtener_tratamiento(self, tratamiento_id):
        """Obtener tratamiento existente o crear uno de prueba"""
        if tratamiento_id:
            try:
                tratamiento = Tratamiento.objects.get(id=tratamiento_id)
                self.stdout.write(f'📋 Usando tratamiento existente ID: {tratamiento.id}')
                return tratamiento
            except Tratamiento.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Tratamiento con ID {tratamiento_id} no encontrado')
                )
                return None

        # Buscar tratamiento activo existente
        tratamiento = Tratamiento.objects.filter(activo=True).first()
        if tratamiento:
            self.stdout.write(f'📋 Usando primer tratamiento activo ID: {tratamiento.id}')
            return tratamiento

        # Crear tratamiento de prueba
        return self.crear_tratamiento_prueba()

    def crear_tratamiento_prueba(self):
        """Crear tratamiento de prueba"""
        self.stdout.write('🔧 Creando tratamiento de prueba...')

        # Buscar paciente
        paciente = PacienteProfile.objects.first()
        if not paciente:
            self.stdout.write(
                self.style.ERROR('❌ No hay pacientes. Crea un paciente primero.')
            )
            return None

        # Buscar episodio
        episodio = EpisodioCefalea.objects.filter(paciente=paciente).first()
        if not episodio:
            self.stdout.write(
                self.style.ERROR('❌ No hay episodios. Crea un episodio primero.')
            )
            return None

        # Crear medicamento
        medicamento, created = Medicamento.objects.get_or_create(
            nombre="Ibuprofeno Test",
            defaults={
                'dosis': '400mg',
                'caracteristica': 'Para testing',
                'hora_de_inicio': datetime.now().time(),
                'frecuencia_horas': 8,
                'duracion_dias': 3
            }
        )

        # Crear tratamiento
        tratamiento = Tratamiento.objects.create(
            episodio=episodio,
            paciente=paciente,
            fecha_inicio=timezone.now().date(),
            activo=True
        )
        tratamiento.medicamentos.add(medicamento)
        tratamiento.asignar_recomendaciones_generales()
        tratamiento.save()

        self.stdout.write(f'✅ Tratamiento creado ID: {tratamiento.id}')
        return tratamiento

    def limpiar_notificaciones(self, tratamiento):
        """Limpiar notificaciones existentes"""
        alertas_count = tratamiento.alertas.count()
        recordatorios_count = tratamiento.recordatorios.count()
        
        tratamiento.alertas.all().delete()
        tratamiento.recordatorios.all().delete()
        
        self.stdout.write(
            f'🧹 Limpiadas {alertas_count} alertas y {recordatorios_count} recordatorios'
        )

    def crear_notificaciones_prueba(self, tratamiento, testing_rapido=False):
        """Crear notificaciones de prueba"""
        self.stdout.write('🔔 Creando notificaciones de prueba...')
        
        ahora = timezone.now()

        # Recordatorio que aparece inmediatamente
        hora_recordatorio = ahora + timedelta(seconds=5)  # 5 segundos después
        
        # Alerta que aparecerá en 3 minutos
        hora_alerta = ahora + timedelta(minutes=3)
        
        recordatorio = Recordatorio.objects.create(
            mensaje="PRUEBA: Recordatorio - En 3 minutos debes tomar tu medicamento",
            fecha_hora=hora_recordatorio,
            estado=EstadoNotificacion.ACTIVO,  # Listo para aparecer cuando llegue su momento
            tratamiento=tratamiento
        )
        
        # Alerta programada para dentro de 3 minutos
        alerta = Alerta.objects.create(
            mensaje="PRUEBA: Es hora de tomar tu Ibuprofeno 400mg",
            fecha_hora=hora_alerta,
            estado=EstadoNotificacion.ACTIVO,  # Listo para aparecer cuando llegue su momento
            tratamiento=tratamiento,
            numero_alerta=1,
            duracion=1,  # 1 minuto de duración por alerta (nuevo)
            tiempo_espera=2  # 2 minutos de espera antes del siguiente reenvío (nuevo)
        )

        self.stdout.write(f'✅ Recordatorio creado ID: {recordatorio.id} - Programado: {hora_recordatorio.strftime("%H:%M:%S")}')
        self.stdout.write(f'✅ Alerta creada ID: {alerta.id} - Programada: {hora_alerta.strftime("%H:%M:%S")}')
        self.stdout.write(f'⏰ Ahora las notificaciones solo aparecerán exactamente a su hora programada')
        self.stdout.write(f'🕐 Hora actual: {ahora.strftime("%H:%M:%S")}')
        self.stdout.write(f'📋 Recordatorio aparecerá a las: {hora_recordatorio.strftime("%H:%M:%S")}')
        self.stdout.write(f'🚨 Alerta aparecerá a las: {hora_alerta.strftime("%H:%M:%S")}')

    def procesar_notificaciones(self, tratamiento):
        """Ejecutar procesamiento de notificaciones"""
        self.stdout.write('⚡ Procesando notificaciones...')
        
        notificaciones_procesadas = tratamiento.procesarNotificacionesPendientes()
        
        self.stdout.write(f'✅ Procesadas {len(notificaciones_procesadas)} notificaciones')
        
        for notif in notificaciones_procesadas:
            tipo = type(notif).__name__
            self.stdout.write(f'   📨 {tipo}: {notif.estado} - {notif.mensaje[:50]}...')

    def mostrar_resumen(self, tratamiento):
        """Mostrar resumen de notificaciones"""
        self.stdout.write('\n📊 RESUMEN DE NOTIFICACIONES:')
        self.stdout.write('=' * 40)

        # Alertas por estado
        alertas = tratamiento.alertas.all()
        for estado in EstadoNotificacion.values:
            count = alertas.filter(estado=estado).count()
            if count > 0:
                self.stdout.write(f'🚨 Alertas {estado}: {count}')

        # Recordatorios por estado
        recordatorios = tratamiento.recordatorios.all()
        for estado in EstadoNotificacion.values:
            count = recordatorios.filter(estado=estado).count()
            if count > 0:
                self.stdout.write(f'📋 Recordatorios {estado}: {count}')

        self.stdout.write(f'\n🎯 ENDPOINTS DE PRUEBA:')
        self.stdout.write(f'GET /api/tratamientos/{tratamiento.id}/notificaciones-pendientes/')
        
        self.stdout.write(f'\n🚀 INSTRUCCIONES PARA TESTING:')
        self.stdout.write(f'1. Ve al Dashboard del frontend (http://localhost:3000 o 5174)')
        self.stdout.write(f'2. El recordatorio aparecerá en 5 segundos')
        self.stdout.write(f'3. La alerta aparecerá exactamente 3 minutos después del recordatorio')
        self.stdout.write(f'4. Ahora las notificaciones respetan su tiempo programado y no aparecen antes')
        self.stdout.write(f'5. Para crear nuevas notificaciones:')
        self.stdout.write(f'   python manage.py generar_notificaciones --tratamiento-id {tratamiento.id} --limpiar')
        self.stdout.write(f'')
        self.stdout.write(f'⏰ CRONOLOGÍA DE TESTING:')
        self.stdout.write(f'   🔔 Recordatorio: Aparece inmediatamente al cargar Dashboard')
        self.stdout.write(f'   🚨 Alerta: Aparece exactamente 3 minutos después')
        
        self.stdout.write(f'\n✨ ¡Listo para probar en el frontend!')
