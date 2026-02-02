# GUÍA: Obtener App Password de Gmail

**Fecha**: 10 de Enero de 2026

## ¿Por qué necesitas una App Password?

Google requiere contraseñas de aplicación específicas para apps de terceros (como este sistema Django) por razones de seguridad.

## Pasos Detallados

### 1. Verificar que tu cuenta Gmail tiene verificación en dos pasos (2FA)

- Ve a: https://myaccount.google.com/security
- Busca "Verificación en dos pasos"
- Si dice "Desactivada", actívala primero:
  - Haz clic en "Verificación en dos pasos"
  - Sigue los pasos (agregar número de teléfono)
  - Completa la configuración

### 2. Generar App Password

Una vez que tienes 2FA activado:

1. **Ve a**: https://myaccount.google.com/apppasswords
   
2. **Inicia sesión** con tu cuenta de Gmail (lucaspy14@gmail.com)

3. **Nombre de la aplicación**: Escribe "Cantina Tita"

4. **Haz clic en "Crear"**

5. **Copia la contraseña**: Aparecerá algo como:
   ```
   abcd efgh ijkl mnop
   ```
   Son **16 caracteres** (4 bloques de 4 letras)

6. **Guarda esta contraseña** - solo se muestra una vez

### 3. Actualizar la configuración

Edita el archivo `.env` en la línea 37:

```dotenv
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

(Sin espacios, los 16 caracteres seguidos)

### 4. Verificar configuración

Ejecuta:
```bash
python configurar_servidor_local.py
```

Y en la sección de prueba de email, envía un email de prueba.

## Alternativa: SendGrid (más profesional)

Si prefieres no usar Gmail (límite de 500 emails/día):

1. **Registrarse**: https://sendgrid.com (100 emails/día gratis)

2. **Crear API Key**:
   - Settings > API Keys > Create API Key
   - Full Access
   - Copiar el key: `SG.xxxxxxxxxxxxxxxxxx`

3. **Actualizar `.env`**:
   ```dotenv
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=SG.tu_api_key_aqui
   ```

## Solución de Problemas

### Error: "Application-specific password required"
- No activaste 2FA en tu cuenta de Gmail
- Activa verificación en dos pasos primero

### Error: "Username and Password not accepted"
- La contraseña es incorrecta
- Genera una nueva App Password
- Copia los 16 caracteres exactos

### Error: "SMTPAuthenticationError"
- Verifica que EMAIL_HOST_USER sea tu email completo
- Verifica que EMAIL_HOST_PASSWORD tenga 16 caracteres
- No uses tu contraseña normal de Gmail, usa la App Password

## Configuración Actual

Tu configuración actual en `.env`:
```
EMAIL_HOST_USER=lucaspy14@gmail.com
EMAIL_HOST_PASSWORD=Eldecano7902  ← INCORRECTO (12 caracteres)
```

**Debe ser**:
```
EMAIL_HOST_USER=lucaspy14@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  ← 16 caracteres de la App Password
```

## Probar la configuración

Una vez actualizado, ejecuta:

```bash
python -c "from django.core.mail import send_mail; send_mail('Prueba', 'Mensaje de prueba', 'lucaspy14@gmail.com', ['tu_otro_email@gmail.com']); print('Email enviado!')"
```

O usa el script completo:
```bash
python configurar_servidor_local.py
```

---

**Referencia**: https://support.google.com/accounts/answer/185833
