"""
Django Management Command para Backup Automático de Base de Datos
Uso: python manage.py backup_database
"""
import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Crea un backup de la base de datos MySQL y limpia backups antiguos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Comprimir el backup con gzip',
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Días de retención de backups (default: 30)',
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Enviar notificación por email',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🔄 INICIANDO BACKUP DE BASE DE DATOS'))
        self.stdout.write('=' * 70)
        
        # Configuración
        db_config = settings.DATABASES['default']
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        compress = options['compress']
        keep_days = options['keep_days']
        notify = options['notify']
        
        # Crear directorio de backups
        backup_dir.mkdir(exist_ok=True)
        
        try:
            # Crear backup
            backup_file = self._create_backup(db_config, backup_dir, compress)
            
            # Limpiar backups antiguos
            deleted_count = self._cleanup_old_backups(backup_dir, keep_days)
            
            # Estadísticas
            total_backups = len(list(backup_dir.glob('backup_*.sql*')))
            backup_size = backup_file.stat().st_size / (1024 * 1024)
            
            self.stdout.write('')
            self.stdout.write('=' * 70)
            self.stdout.write(self.style.SUCCESS('✅ BACKUP COMPLETADO EXITOSAMENTE'))
            self.stdout.write('=' * 70)
            self.stdout.write(f'📄 Archivo: {backup_file.name}')
            self.stdout.write(f'💾 Tamaño: {backup_size:.2f} MB')
            self.stdout.write(f'📁 Total backups: {total_backups}')
            self.stdout.write(f'🗑️  Backups eliminados: {deleted_count}')
            self.stdout.write('=' * 70)
            
            # Enviar notificación por email
            if notify:
                self._send_notification(backup_file, backup_size, total_backups)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante backup: {str(e)}'))
            raise CommandError(f'Backup falló: {str(e)}')

    def _create_backup(self, db_config, backup_dir, compress=False):
        """Crear backup de la base de datos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{db_config["NAME"]}_{timestamp}.sql'
        
        self.stdout.write(f'📊 Base de datos: {db_config["NAME"]}')
        self.stdout.write(f'🖥️  Host: {db_config["HOST"]}')
        self.stdout.write(f'📁 Directorio: {backup_dir}')
        self.stdout.write('')
        
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={db_config["HOST"]}',
            f'--port={db_config["PORT"]}',
            f'--user={db_config["USER"]}',
            '--single-transaction',
            '--quick',
            '--lock-tables=false',
            '--routines',
            '--triggers',
            '--events',
            f'--result-file={backup_file}',
            db_config['NAME']
        ]
        
        # Agregar password si existe
        if db_config.get('PASSWORD'):
            cmd.insert(4, f'--password={db_config["PASSWORD"]}')
        
        self.stdout.write('🔄 Ejecutando mysqldump...')
        
        # Ejecutar backup
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise Exception(f'mysqldump falló: {result.stderr}')
        
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(f'✅ Backup creado: {size_mb:.2f} MB'))
        
        # Comprimir si se solicitó
        if compress:
            self.stdout.write('🗜️  Comprimiendo archivo...')
            backup_gz = Path(str(backup_file) + '.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(backup_gz, 'wb', compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar archivo sin comprimir
            backup_file.unlink()
            
            size_gz_mb = backup_gz.stat().st_size / (1024 * 1024)
            ratio = (1 - size_gz_mb / size_mb) * 100
            self.stdout.write(self.style.SUCCESS(
                f'✅ Comprimido: {size_gz_mb:.2f} MB (reducción: {ratio:.1f}%)'
            ))
            
            return backup_gz
        
        return backup_file

    def _cleanup_old_backups(self, backup_dir, keep_days):
        """Eliminar backups más antiguos que keep_days"""
        self.stdout.write(f'\n🧹 Limpiando backups más antiguos que {keep_days} días...')
        
        fecha_limite = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for archivo in backup_dir.glob('backup_*.sql*'):
            fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime)
            
            if fecha_archivo < fecha_limite:
                try:
                    size_mb = archivo.stat().st_size / (1024 * 1024)
                    archivo.unlink()
                    deleted_count += 1
                    self.stdout.write(f'  🗑️  Eliminado: {archivo.name} ({size_mb:.2f} MB)')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  No se pudo eliminar {archivo.name}: {e}')
                    )
        
        if deleted_count == 0:
            self.stdout.write('  ℹ️  No hay backups antiguos para eliminar')
        
        return deleted_count

    def _send_notification(self, backup_file, backup_size, total_backups):
        """Enviar notificación por email"""
        try:
            subject = f'✅ Backup Completado - {datetime.now().strftime("%d/%m/%Y %H:%M")}'
            message = f"""
Backup de base de datos completado exitosamente.

Detalles:
- Archivo: {backup_file.name}
- Tamaño: {backup_size:.2f} MB
- Total backups: {total_backups}
- Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Sistema de Backup Automático - Cantina POS
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('📧 Notificación enviada'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  No se pudo enviar notificación: {e}'))
