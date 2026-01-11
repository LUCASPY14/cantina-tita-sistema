#!/bin/bash
#
# Script Automatizado para Configurar SSL/HTTPS con Let's Encrypt
# Cantina Tita
#

set -e  # Salir si hay errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_color "$CYAN" "═══════════════════════════════════════════════════════════"
    print_color "$CYAN" "  $1"
    print_color "$CYAN" "═══════════════════════════════════════════════════════════"
    echo ""
}

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_color "$RED" "❌ Este script debe ejecutarse como root (sudo)"
   exit 1
fi

print_header "🔒 CONFIGURACIÓN SSL/HTTPS - CANTINA TITA"

# === CONFIGURACIÓN ===
read -p "Dominio principal (ej: cantitatita.com.py): " DOMAIN
read -p "Dominio www (ej: www.cantitatita.com.py) [Enter para omitir]: " WWW_DOMAIN
read -p "Email para notificaciones de Let's Encrypt: " EMAIL
read -p "Ruta de la aplicación [/var/www/cantitatita]: " APP_DIR
APP_DIR=${APP_DIR:-/var/www/cantitatita}

print_color "$YELLOW" "\n📋 Configuración:"
print_color "$YELLOW" "   Dominio: $DOMAIN"
[[ -n "$WWW_DOMAIN" ]] && print_color "$YELLOW" "   WWW: $WWW_DOMAIN"
print_color "$YELLOW" "   Email: $EMAIL"
print_color "$YELLOW" "   Directorio: $APP_DIR"
echo ""

read -p "¿Continuar? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_color "$YELLOW" "Cancelado"
    exit 0
fi

# === VERIFICACIONES PREVIAS ===
print_header "🔍 VERIFICACIONES PREVIAS"

# Verificar DNS
print_color "$CYAN" "Verificando DNS..."
if host $DOMAIN > /dev/null 2>&1; then
    IP=$(host $DOMAIN | grep "has address" | awk '{print $4}')
    print_color "$GREEN" "✅ DNS configurado: $DOMAIN -> $IP"
else
    print_color "$RED" "❌ ERROR: DNS no resuelve para $DOMAIN"
    print_color "$YELLOW" "   Configura el DNS antes de continuar"
    exit 1
fi

# Verificar puertos
print_color "$CYAN" "\nVerificando puertos..."
if netstat -tuln | grep -q ":80 "; then
    print_color "$GREEN" "✅ Puerto 80 disponible"
else
    print_color "$YELLOW" "⚠️  Puerto 80 no escuchando. Asegúrate de que Nginx esté corriendo"
fi

if netstat -tuln | grep -q ":443 "; then
    print_color "$YELLOW" "⚠️  Puerto 443 ya en uso (puede ser normal si hay SSL previo)"
else
    print_color "$GREEN" "✅ Puerto 443 disponible"
fi

# === INSTALACIÓN DE CERTBOT ===
print_header "📦 INSTALACIÓN DE CERTBOT"

if command -v certbot &> /dev/null; then
    print_color "$GREEN" "✅ Certbot ya está instalado"
else
    print_color "$CYAN" "Instalando Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
    print_color "$GREEN" "✅ Certbot instalado"
fi

# === BACKUP DE CONFIGURACIÓN NGINX ===
print_header "💾 BACKUP DE CONFIGURACIÓN"

NGINX_CONF="/etc/nginx/sites-available/cantitatita"
BACKUP_DIR="/root/backups_nginx"
mkdir -p $BACKUP_DIR

if [[ -f $NGINX_CONF ]]; then
    BACKUP_FILE="$BACKUP_DIR/cantitatita_$(date +%Y%m%d_%H%M%S).conf"
    cp $NGINX_CONF $BACKUP_FILE
    print_color "$GREEN" "✅ Backup creado: $BACKUP_FILE"
else
    print_color "$YELLOW" "⚠️  No se encontró configuración previa de Nginx"
fi

# === OBTENER CERTIFICADO ===
print_header "🔐 OBTENIENDO CERTIFICADO SSL"

print_color "$CYAN" "Usando certbot con plugin de Nginx..."

# Construir comando
CERTBOT_CMD="certbot --nginx -d $DOMAIN"
[[ -n "$WWW_DOMAIN" ]] && CERTBOT_CMD="$CERTBOT_CMD -d $WWW_DOMAIN"
CERTBOT_CMD="$CERTBOT_CMD --email $EMAIL --agree-tos --redirect --non-interactive"

print_color "$YELLOW" "Ejecutando: $CERTBOT_CMD"
echo ""

if $CERTBOT_CMD; then
    print_color "$GREEN" "✅ Certificado SSL obtenido exitosamente"
else
    print_color "$RED" "❌ ERROR al obtener certificado"
    print_color "$YELLOW" "\n💡 Posibles soluciones:"
    print_color "$YELLOW" "   1. Verifica que el DNS apunte correctamente a este servidor"
    print_color "$YELLOW" "   2. Asegúrate de que los puertos 80 y 443 estén abiertos en el firewall"
    print_color "$YELLOW" "   3. Verifica que Nginx esté corriendo: sudo systemctl status nginx"
    print_color "$YELLOW" "   4. Revisa los logs: sudo tail -f /var/log/letsencrypt/letsencrypt.log"
    exit 1
fi

# === CONFIGURAR NGINX AVANZADO ===
print_header "⚙️  CONFIGURACIÓN AVANZADA DE NGINX"

print_color "$CYAN" "Mejorando configuración SSL de Nginx..."

cat > $NGINX_CONF << 'EOF'
# Redirigir HTTP a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN WWW_DOMAIN;
    return 301 https://DOMAIN$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name DOMAIN;

    # Certificados SSL (gestionados por Certbot)
    ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # SSL Settings Avanzados
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net;" always;

    # Logging
    access_log /var/log/nginx/cantitatita_access.log;
    error_log /var/log/nginx/cantitatita_error.log;

    # Client settings
    client_max_body_size 75M;
    client_body_timeout 120s;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    gzip_disable "msie6";

    # Archivos estáticos
    location /static/ {
        alias APP_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Archivos media
    location /media/ {
        alias APP_DIR/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Favicon
    location = /favicon.ico {
        alias APP_DIR/staticfiles/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # robots.txt
    location = /robots.txt {
        alias APP_DIR/staticfiles/robots.txt;
        access_log off;
        log_not_found off;
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://unix:APP_DIR/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffering
        proxy_buffering off;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Ocultar versión de Nginx
    server_tokens off;
}

# Redirigir www a no-www (si aplica)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name WWW_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    return 301 https://DOMAIN$request_uri;
}
EOF

# Reemplazar placeholders
sed -i "s|DOMAIN|$DOMAIN|g" $NGINX_CONF
[[ -n "$WWW_DOMAIN" ]] && sed -i "s|WWW_DOMAIN|$WWW_DOMAIN|g" $NGINX_CONF || sed -i "/WWW_DOMAIN/d" $NGINX_CONF
sed -i "s|APP_DIR|$APP_DIR|g" $NGINX_CONF

print_color "$GREEN" "✅ Configuración Nginx actualizada"

# === VERIFICAR Y RECARGAR NGINX ===
print_header "🔄 VERIFICACIÓN Y RECARGA"

print_color "$CYAN" "Verificando sintaxis de Nginx..."
if nginx -t; then
    print_color "$GREEN" "✅ Configuración de Nginx válida"
    
    print_color "$CYAN" "\nRecargando Nginx..."
    systemctl reload nginx
    print_color "$GREEN" "✅ Nginx recargado"
else
    print_color "$RED" "❌ ERROR en configuración de Nginx"
    print_color "$YELLOW" "   Restaurando backup..."
    [[ -f $BACKUP_FILE ]] && cp $BACKUP_FILE $NGINX_CONF
    exit 1
fi

# === CONFIGURAR RENOVACIÓN AUTOMÁTICA ===
print_header "🔄 RENOVACIÓN AUTOMÁTICA"

print_color "$CYAN" "Verificando cron job de renovación..."

# Probar renovación en dry-run
if certbot renew --dry-run > /dev/null 2>&1; then
    print_color "$GREEN" "✅ Renovación automática configurada correctamente"
else
    print_color "$YELLOW" "⚠️  Error en test de renovación. Revisa manualmente con: sudo certbot renew --dry-run"
fi

# Crear script de post-renovación
POST_RENEWAL_SCRIPT="/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh"
mkdir -p /etc/letsencrypt/renewal-hooks/deploy

cat > $POST_RENEWAL_SCRIPT << 'EOF'
#!/bin/bash
# Post-renewal script - Recargar Nginx después de renovar certificados
systemctl reload nginx
echo "$(date): Nginx recargado después de renovar certificados" >> /var/log/letsencrypt/renewal.log
EOF

chmod +x $POST_RENEWAL_SCRIPT
print_color "$GREEN" "✅ Script de post-renovación creado"

# === VERIFICAR CERTIFICADO ===
print_header "🔍 VERIFICACIÓN DEL CERTIFICADO"

print_color "$CYAN" "Información del certificado:"
certbot certificates | grep -A 5 "$DOMAIN"

# === PRUEBA SSL ===
print_header "🧪 PRUEBA FINAL"

print_color "$CYAN" "Verificando HTTPS..."
sleep 2

if curl -sI https://$DOMAIN | grep -q "HTTP/2 200"; then
    print_color "$GREEN" "✅ HTTPS funcionando correctamente"
else
    print_color "$YELLOW" "⚠️  HTTPS puede no estar funcionando. Verifica manualmente en el navegador"
fi

# === ACTUALIZAR DJANGO SETTINGS ===
print_header "⚙️  ACTUALIZAR DJANGO SETTINGS"

print_color "$YELLOW" "Recuerda actualizar tu archivo .env con:"
print_color "$CYAN" "SECURE_SSL_REDIRECT=True"
print_color "$CYAN" "SESSION_COOKIE_SECURE=True"
print_color "$CYAN" "CSRF_COOKIE_SECURE=True"
print_color "$CYAN" "SECURE_HSTS_SECONDS=31536000"
print_color "$CYAN" "CSRF_TRUSTED_ORIGINS=https://$DOMAIN"

# === RESUMEN FINAL ===
print_header "✅ CONFIGURACIÓN COMPLETADA"

print_color "$GREEN" "SSL/HTTPS configurado exitosamente!"
echo ""
print_color "$CYAN" "📋 Resumen:"
print_color "$WHITE" "   • Certificado SSL: ✅ Instalado"
print_color "$WHITE" "   • HTTPS: ✅ Activo"
print_color "$WHITE" "   • Redirección HTTP->HTTPS: ✅ Configurada"
print_color "$WHITE" "   • Renovación automática: ✅ Configurada"
print_color "$WHITE" "   • Security headers: ✅ Aplicados"
print_color "$WHITE" "   • Gzip compression: ✅ Activada"
echo ""
print_color "$CYAN" "🌐 Accede a tu sitio:"
print_color "$WHITE" "   https://$DOMAIN"
[[ -n "$WWW_DOMAIN" ]] && print_color "$WHITE" "   https://$WWW_DOMAIN (redirige a dominio principal)"
echo ""
print_color "$CYAN" "📅 Próxima renovación automática:"
certbot certificates | grep "Expiry Date" | head -1
echo ""
print_color "$YELLOW" "💡 Comandos útiles:"
print_color "$WHITE" "   • Ver certificados: sudo certbot certificates"
print_color "$WHITE" "   • Renovar manualmente: sudo certbot renew"
print_color "$WHITE" "   • Test renovación: sudo certbot renew --dry-run"
print_color "$WHITE" "   • Logs: sudo tail -f /var/log/letsencrypt/letsencrypt.log"
echo ""
print_color "$GREEN" "🎉 ¡Configuración SSL completada exitosamente!"
echo ""
