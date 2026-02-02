"""
Sistema de Monitoring y Health Checks para Cantina POS
Monitorea: BD, Redis, Disco, Memoria, CPU, APIs
"""
import os
import time
import psutil
import pymysql
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Ejecuta health checks del sistema y envía alertas si es necesario'

    # Umbrales de alerta
    THRESHOLDS = {
        'disk_usage': 80,      # % uso de disco
        'memory_usage': 85,    # % uso de memoria
        'cpu_usage': 90,       # % uso de CPU
        'db_connections': 80,  # % de conexiones BD
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Enviar notificación por email si hay problemas',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        notify = options['notify']
        verbose = options['verbose']
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🏥 HEALTH CHECK DEL SISTEMA'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        self.stdout.write('')
        
        # Ejecutar todos los checks
        results = {}
        alerts = []
        
        # 1. Check Base de Datos
        db_status, db_details = self._check_database()
        results['database'] = {'status': db_status, 'details': db_details}
        if not db_status:
            alerts.append(f'❌ Base de Datos: {db_details}')
        
        # 2. Check Redis/Cache
        cache_status, cache_details = self._check_cache()
        results['cache'] = {'status': cache_status, 'details': cache_details}
        if not cache_status:
            alerts.append(f'⚠️  Cache: {cache_details}')
        
        # 3. Check Disco
        disk_status, disk_details = self._check_disk()
        results['disk'] = {'status': disk_status, 'details': disk_details}
        if not disk_status:
            alerts.append(f'⚠️  Disco: {disk_details}')
        
        # 4. Check Memoria
        memory_status, memory_details = self._check_memory()
        results['memory'] = {'status': memory_status, 'details': memory_details}
        if not memory_status:
            alerts.append(f'⚠️  Memoria: {memory_details}')
        
        # 5. Check CPU
        cpu_status, cpu_details = self._check_cpu()
        results['cpu'] = {'status': cpu_status, 'details': cpu_details}
        if not cpu_status:
            alerts.append(f'⚠️  CPU: {cpu_details}')
        
        # 6. Check Directorio de Backups
        backup_status, backup_details = self._check_backups()
        results['backups'] = {'status': backup_status, 'details': backup_details}
        if not backup_status:
            alerts.append(f'⚠️  Backups: {backup_details}')
        
        # Mostrar resultados
        self._display_results(results, verbose)
        
        # Enviar alertas si hay problemas
        if alerts and notify:
            self._send_alerts(alerts)
        
        # Resumen final
        self.stdout.write('')
        self.stdout.write('=' * 70)
        if alerts:
            self.stdout.write(self.style.WARNING(f'⚠️  {len(alerts)} ALERTA(S) DETECTADA(S)'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ TODOS LOS CHECKS PASARON'))
        self.stdout.write('=' * 70)

    def _check_database(self) -> Tuple[bool, str]:
        """Verificar conexión y estado de la base de datos"""
        try:
            db_config = settings.DATABASES['default']
            
            # Conectar a MySQL
            connection = pymysql.connect(
                host=db_config['HOST'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                database=db_config['NAME'],
                port=int(db_config['PORT'])
            )
            
            cursor = connection.cursor()
            
            # Obtener número de conexiones
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            threads_connected = int(cursor.fetchone()[1])
            
            cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
            max_connections = int(cursor.fetchone()[1])
            
            usage_percent = (threads_connected / max_connections) * 100
            
            cursor.close()
            connection.close()
            
            self.stdout.write(self.style.SUCCESS('  ✅ Base de Datos: Conectado'))
            self.stdout.write(f'     Conexiones: {threads_connected}/{max_connections} ({usage_percent:.1f}%)')
            
            # Alerta si uso > 80%
            if usage_percent > self.THRESHOLDS['db_connections']:
                return False, f'Alto uso de conexiones: {usage_percent:.1f}%'
            
            return True, f'{threads_connected}/{max_connections} conexiones'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Base de Datos: Error'))
            self.stdout.write(f'     {str(e)}')
            return False, str(e)

    def _check_cache(self) -> Tuple[bool, str]:
        """Verificar sistema de caché"""
        try:
            # Test de cache
            test_key = 'health_check_test'
            test_value = datetime.now().isoformat()
            
            cache.set(test_key, test_value, 10)
            cached_value = cache.get(test_key)
            
            if cached_value == test_value:
                self.stdout.write(self.style.SUCCESS('  ✅ Cache: Funcionando'))
                cache.delete(test_key)
                return True, 'Cache OK'
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  Cache: No responde correctamente'))
                return False, 'Cache no guarda valores correctamente'
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Cache: {str(e)}'))
            return False, str(e)

    def _check_disk(self) -> Tuple[bool, str]:
        """Verificar espacio en disco"""
        try:
            disk = psutil.disk_usage(str(settings.BASE_DIR))
            usage_percent = disk.percent
            
            status_icon = '✅' if usage_percent < self.THRESHOLDS['disk_usage'] else '⚠️'
            status_style = self.style.SUCCESS if usage_percent < self.THRESHOLDS['disk_usage'] else self.style.WARNING
            
            self.stdout.write(status_style(f'  {status_icon} Disco: {usage_percent:.1f}% usado'))
            self.stdout.write(f'     Libre: {disk.free / (1024**3):.1f} GB de {disk.total / (1024**3):.1f} GB')
            
            if usage_percent > self.THRESHOLDS['disk_usage']:
                return False, f'Disco al {usage_percent:.1f}% de capacidad'
            
            return True, f'{usage_percent:.1f}% usado'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Disco: Error - {str(e)}'))
            return False, str(e)

    def _check_memory(self) -> Tuple[bool, str]:
        """Verificar uso de memoria RAM"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            status_icon = '✅' if usage_percent < self.THRESHOLDS['memory_usage'] else '⚠️'
            status_style = self.style.SUCCESS if usage_percent < self.THRESHOLDS['memory_usage'] else self.style.WARNING
            
            self.stdout.write(status_style(f'  {status_icon} Memoria: {usage_percent:.1f}% usado'))
            self.stdout.write(f'     Disponible: {memory.available / (1024**3):.1f} GB de {memory.total / (1024**3):.1f} GB')
            
            if usage_percent > self.THRESHOLDS['memory_usage']:
                return False, f'Memoria al {usage_percent:.1f}%'
            
            return True, f'{usage_percent:.1f}% usado'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Memoria: Error - {str(e)}'))
            return False, str(e)

    def _check_cpu(self) -> Tuple[bool, str]:
        """Verificar uso de CPU"""
        try:
            # Medir CPU durante 1 segundo
            cpu_percent = psutil.cpu_percent(interval=1)
            
            status_icon = '✅' if cpu_percent < self.THRESHOLDS['cpu_usage'] else '⚠️'
            status_style = self.style.SUCCESS if cpu_percent < self.THRESHOLDS['cpu_usage'] else self.style.WARNING
            
            self.stdout.write(status_style(f'  {status_icon} CPU: {cpu_percent:.1f}% usado'))
            self.stdout.write(f'     Cores: {psutil.cpu_count(logical=True)} (lógicos)')
            
            if cpu_percent > self.THRESHOLDS['cpu_usage']:
                return False, f'CPU al {cpu_percent:.1f}%'
            
            return True, f'{cpu_percent:.1f}% usado'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ CPU: Error - {str(e)}'))
            return False, str(e)

    def _check_backups(self) -> Tuple[bool, str]:
        """Verificar que existan backups recientes"""
        try:
            backup_dir = Path(settings.BASE_DIR) / 'backups'
            
            if not backup_dir.exists():
                self.stdout.write(self.style.WARNING('  ⚠️  Backups: Directorio no existe'))
                return False, 'Directorio de backups no existe'
            
            # Buscar backups recientes (últimas 24 horas)
            backup_files = list(backup_dir.glob('backup_*.sql*'))
            
            if not backup_files:
                self.stdout.write(self.style.WARNING('  ⚠️  Backups: No hay backups'))
                return False, 'No hay backups disponibles'
            
            # Obtener el backup más reciente
            latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
            backup_age_hours = (time.time() - latest_backup.stat().st_mtime) / 3600
            
            status_icon = '✅' if backup_age_hours < 24 else '⚠️'
            status_style = self.style.SUCCESS if backup_age_hours < 24 else self.style.WARNING
            
            self.stdout.write(status_style(f'  {status_icon} Backups: {len(backup_files)} archivo(s)'))
            self.stdout.write(f'     Último: hace {backup_age_hours:.1f} horas')
            
            if backup_age_hours > 24:
                return False, f'Último backup hace {backup_age_hours:.1f} horas'
            
            return True, f'{len(backup_files)} backups disponibles'
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Backups: {str(e)}'))
            return False, str(e)

    def _display_results(self, results: Dict, verbose: bool):
        """Mostrar resultados de los checks"""
        if verbose:
            self.stdout.write('')
            self.stdout.write('📊 DETALLES COMPLETOS:')
            for component, data in results.items():
                status = '✅ OK' if data['status'] else '❌ ERROR'
                self.stdout.write(f'  {component.upper()}: {status} - {data["details"]}')

    def _send_alerts(self, alerts: List[str]):
        """Enviar alertas por email"""
        try:
            subject = f'⚠️  Alertas del Sistema - {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            message = f"""
Se han detectado problemas en el sistema:

{''.join([f'- {alert}\\n' for alert in alerts])}

Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Por favor revisar el sistema.

Sistema de Monitoring - Cantina POS
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('📧 Alerta enviada por email'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  No se pudo enviar alerta: {e}'))
