# ✅ Checklist Completo de Deployment

**Sistema:** Cantina Tita  
**Versión:** 1.0  
**Fecha:** 4 de Febrero 2026

---

## 🎯 FASE 1: PREPARACIÓN PRE-DEPLOYMENT

### Código y Repositorio
- [ ] Todos los cambios commiteados a Git
- [ ] Branch `development` actualizado
- [ ] Tests pasando (188/188)
- [ ] `python manage.py check --deploy` sin errores críticos
- [ ] Código pusheado a GitHub

### Base de Datos
- [ ] Backup de base de datos creado
  ```bash
  python backend/manage.py backup_database --compress
  ```
- [ ] Ubicación del backup documentada
- [ ] Migraciones aplicadas sin errores
  ```bash
  python backend/manage.py migrate --check
  ```

### Configuración de Producción
- [ ] Archivo `.env.production` creado
- [ ] SECRET_KEY única generada (50+ caracteres)
- [ ] DEBUG=False configurado
- [ ] ALLOWED_HOSTS con dominio/IP real
- [ ] DB_PASSWORD configurado (no placeholder)
- [ ] EMAIL_HOST_PASSWORD configurado (App Password)
- [ ] RECAPTCHA_PUBLIC_KEY y PRIVATE_KEY (producción)

### Verificación de Seguridad
- [ ] Ejecutado: `python verificar_produccion.py`
- [ ] Resultado: ✅ LISTO PARA PRODUCCIÓN (o advertencias aceptables)
- [ ] Contraseñas seguras (20+ caracteres)
- [ ] No hay credenciales hardcodeadas en código

---

## 🚀 FASE 2: DEPLOYMENT (según opción elegida)

### Opción A: Railway
- [ ] Cuenta de Railway creada
- [ ] Proyecto conectado a GitHub
- [ ] Variables de entorno configuradas en Dashboard
- [ ] MySQL database creada
- [ ] Primera build exitosa
- [ ] URL de Railway accesible: `https://_____.railway.app`
- [ ] Dominio personalizado configurado (si aplica)

### Opción B: Render
- [ ] Cuenta de Render creada
- [ ] Web Service creado desde GitHub
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL database creada
- [ ] Primera build exitosa
- [ ] URL de Render accesible: `https://_____.onrender.com`

### Opción C: VPS
- [ ] VPS provisionado (IP: _______________)
- [ ] SSH configurado y accesible
- [ ] Usuario no-root creado
- [ ] Python 3.11+ instalado
- [ ] MySQL/PostgreSQL instalado y configurado
- [ ] Nginx instalado
- [ ] Repositorio clonado en `/var/www/`
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Gunicorn service configurado
- [ ] Nginx configurado
- [ ] Firewall configurado (puertos 80, 443, 22)

### Opción D: Servidor Local
- [ ] Servidor configurado con IP estática local
- [ ] Gunicorn corriendo
- [ ] Accesible desde red local
- [ ] DynDNS configurado (si requiere acceso externo)
- [ ] Port forwarding configurado en router

---

## 🔒 FASE 3: CONFIGURACIÓN SSL/HTTPS (si aplica)

### Railway/Render
- [ ] SSL configurado automáticamente por la plataforma
- [ ] HTTPS funciona correctamente
- [ ] Redirect HTTP → HTTPS activo

### VPS
- [ ] Certbot instalado
- [ ] Certificado SSL obtenido con Let's Encrypt
  ```bash
  sudo certbot --nginx -d tu-dominio.com
  ```
- [ ] Nginx configurado para HTTPS
- [ ] Verificación SSL Labs: Grado A o A+
  - URL: https://www.ssllabs.com/ssltest/
- [ ] Renovación automática configurada
  ```bash
  sudo certbot renew --dry-run
  ```
- [ ] `.env.production` actualizado con configuraciones SSL:
  - [ ] SECURE_SSL_REDIRECT=True
  - [ ] SESSION_COOKIE_SECURE=True
  - [ ] CSRF_COOKIE_SECURE=True
  - [ ] SECURE_HSTS_SECONDS=31536000

---

## 🧪 FASE 4: TESTING POST-DEPLOYMENT

### Accesibilidad
- [ ] Sitio accesible vía HTTPS
  - URL: https://___________________________
- [ ] No aparecen errores 500/502/503
- [ ] Static files cargando correctamente (CSS, JS, imágenes)
- [ ] Media files accesibles

### Funcionalidades Críticas
- [ ] **Admin Panel**
  - [ ] Login funciona: `/admin`
  - [ ] Superusuario puede acceder
  - [ ] Tablas visibles y editables

- [ ] **Sistema POS**
  - [ ] Crear venta de prueba
  - [ ] Aplicar pago
  - [ ] Generar factura
  - [ ] Cerrar caja

- [ ] **Portal de Padres**
  - [ ] Registro de nuevo usuario
  - [ ] Login funciona
  - [ ] Ver saldo de hijo
  - [ ] Realizar recarga

- [ ] **Tarjetas RFID**
  - [ ] Registrar tarjeta
  - [ ] Asociar a estudiante
  - [ ] Realizar consumo de prueba

- [ ] **Sistema de Emails**
  - [ ] Envío de email de prueba
    ```python
    python manage.py shell
    >>> from django.core.mail import send_mail
    >>> send_mail('Test', 'Mensaje', 'from@example.com', ['to@example.com'])
    ```
  - [ ] Email recibido correctamente
  - [ ] Notificaciones de recarga funcionan

- [ ] **reCAPTCHA**
  - [ ] Formulario de login muestra reCAPTCHA
  - [ ] Validación funciona (no aparece error de claves)

### Performance
- [ ] Página de inicio carga en < 3 segundos
- [ ] Dashboard carga en < 5 segundos
- [ ] Sin errores en consola del navegador (F12)

---

## 📊 FASE 5: CONFIGURACIÓN POST-DEPLOYMENT

### Backups Automáticos
- [ ] Script de backup configurado
- [ ] Cron job/scheduled task creado
  ```bash
  # Ejemplo cron (diario a las 2am):
  0 2 * * * /path/to/venv/bin/python /path/to/manage.py backup_database --compress --notify
  ```
- [ ] Primer backup ejecutado manualmente
- [ ] Backup verificado (archivo existe y es válido)
- [ ] Ubicación de backups documentada

### Monitoreo (Opcional pero Recomendado)
- [ ] **Sentry** configurado para tracking de errores
  - [ ] DSN configurado en settings.py
  - [ ] Error de prueba enviado y visible en Sentry

- [ ] **UptimeRobot** configurado
  - [ ] Check cada 5 minutos
  - [ ] Alertas por email configuradas
  - [ ] Primer check exitoso

- [ ] **Logs** configurados
  - [ ] Logs de aplicación rotando (no crecen infinitamente)
  - [ ] Logs de Nginx/Apache configurados
  - [ ] Ubicación de logs documentada

### Seguridad Adicional
- [ ] Firewall configurado (UFW/firewalld)
  ```bash
  sudo ufw allow 22    # SSH
  sudo ufw allow 80    # HTTP
  sudo ufw allow 443   # HTTPS
  sudo ufw enable
  ```
- [ ] Fail2ban instalado (VPS)
  ```bash
  sudo apt install fail2ban
  ```
- [ ] Rate limiting configurado en Nginx
- [ ] Actualizaciones de sistema configuradas
  ```bash
  sudo apt install unattended-upgrades
  ```

---

## 📖 FASE 6: DOCUMENTACIÓN

### Documentación Técnica
- [ ] URL de producción documentada
- [ ] Credenciales de admin documentadas (seguras)
- [ ] Ubicación de backups documentada
- [ ] Procedimiento de actualización documentado
- [ ] Contactos de soporte documentados

### Documentación de Usuario
- [ ] Manual de usuario del POS creado/actualizado
- [ ] Guía del portal de padres creada
- [ ] Video tutoriales grabados (opcional)
- [ ] FAQ actualizado

### Archivo de Configuración
Crear archivo `PRODUCCION.md` en raíz con:

```markdown
# Configuración de Producción

**URL:** https://___________________________
**Servidor:** ___________________________
**IP:** ___________________________

## Credenciales
- Admin user: ___________________________
- MySQL user: cantina_user
- MySQL database: cantitatitadb

## Ubicaciones
- Proyecto: /var/www/cantina-tita-sistema
- Logs: /var/www/cantina-tita-sistema/backend/logs
- Backups: /var/backups/cantina
- Static files: /var/www/cantina-tita-sistema/backend/staticfiles

## Servicios
- Gunicorn: systemctl status gunicorn
- Nginx: systemctl status nginx
- MySQL: systemctl status mysql

## Contactos
- Soporte técnico: ___________________________
- Proveedor hosting: ___________________________
- DNS proveedor: ___________________________
```

---

## 🎓 FASE 7: CAPACITACIÓN Y LANZAMIENTO

### Personal de Cantina
- [ ] Capacitación en sistema POS completada
- [ ] Capacitación en cierre de caja
- [ ] Capacitación en registro de tarjetas
- [ ] Manual de procedimientos entregado
- [ ] Preguntas respondidas

### Padres/Tutores
- [ ] Email de bienvenida enviado con:
  - [ ] URL del portal
  - [ ] Instrucciones de registro
  - [ ] Guía de recargas
  - [ ] Contacto de soporte
- [ ] Reunión informativa realizada (si aplica)

### Estudiantes
- [ ] Tarjetas RFID distribuidas
- [ ] Instrucciones de uso entregadas
- [ ] Demostración en vivo realizada

---

## 🔄 FASE 8: MONITOREO INICIAL (Primera Semana)

### Día 1
- [ ] Verificar uptime cada hora
- [ ] Revisar logs de errores
- [ ] Responder consultas de usuarios
- [ ] Documentar problemas encontrados

### Día 2-3
- [ ] Verificar uptime cada 3 horas
- [ ] Analizar performance
- [ ] Verificar que backups se ejecutaron
- [ ] Ajustar configuraciones si es necesario

### Día 4-7
- [ ] Verificar uptime diariamente
- [ ] Revisar logs diariamente
- [ ] Recopilar feedback de usuarios
- [ ] Planificar mejoras

---

## ✅ CHECKLIST DE CIERRE

### Técnico
- [ ] Sistema estable por 7 días consecutivos
- [ ] Uptime > 99.9%
- [ ] Todos los tests automatizados pasando
- [ ] Backups ejecutándose correctamente
- [ ] No hay errores críticos en logs

### Negocio
- [ ] Personal capacitado y usando el sistema
- [ ] Padres/tutores registrados en portal
- [ ] Primeras ventas/recargas realizadas exitosamente
- [ ] Feedback inicial recopilado
- [ ] Cliente satisfecho con el sistema

### Administrativo
- [ ] Documentación completa entregada
- [ ] Accesos y credenciales transferidos
- [ ] Procedimientos de mantenimiento documentados
- [ ] Plan de soporte definido
- [ ] Contrato/acuerdo firmado (si aplica)

---

## 🎉 DEPLOYMENT COMPLETADO

**Fecha de deployment:** ____ / ____ / ______

**Deployed por:** _______________________________

**Aprobado por:** _______________________________

**Siguiente revisión programada:** ____ / ____ / ______

---

## 📞 CONTACTOS DE EMERGENCIA

### Soporte Técnico
- **Desarrollador:** _______________________________
- **Email:** _______________________________
- **Teléfono:** _______________________________

### Infraestructura
- **Hosting provider:** _______________________________
- **Soporte técnico hosting:** _______________________________
- **Proveedor DNS:** _______________________________

### Servicios Externos
- **Email (Gmail/SendGrid):** _______________________________
- **Monitoreo (Sentry):** _______________________________
- **Backups:** _______________________________

---

**Notas adicionales:**
```
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
```

---

**🎊 ¡Felicitaciones por el deployment exitoso!**

Este checklist está diseñado para garantizar un deployment completo y sin problemas. Revisa cada ítem cuidadosamente antes de marcarlo como completado.
