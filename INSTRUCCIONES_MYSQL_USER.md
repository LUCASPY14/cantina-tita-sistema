# 🔧 Crear Usuario MySQL - Instrucciones Paso a Paso

## Paso 1: Abrir MySQL Workbench

1. Abre **MySQL Workbench** (el programa que usas normalmente)
2. Conecta con el usuario **root** y tu password: `L01G05S33Vice.42`

---

## Paso 2: Ejecutar este Script SQL

Copia y pega EXACTAMENTE este código en el Query Editor:

```sql
-- Eliminar usuario si ya existe (por si acaso)
DROP USER IF EXISTS 'cantina_user'@'localhost';

-- Crear usuario con password seguro
CREATE USER 'cantina_user'@'localhost' IDENTIFIED BY 'L01G05S33Vice.42';

-- Dar permisos SOLO sobre la base de datos cantitatitadb
GRANT ALL PRIVILEGES ON cantitatitadb.* TO 'cantina_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar que el usuario fue creado
SELECT User, Host FROM mysql.user WHERE User = 'cantina_user';

-- Verificar permisos
SHOW GRANTS FOR 'cantina_user'@'localhost';
```

---

## Paso 3: Ejecutar el Script

1. Presiona el **rayo** (Execute) o presiona `Ctrl + Shift + Enter`
2. Verás en la salida:
   ```
   User           | Host
   cantina_user   | localhost
   
   GRANT ALL PRIVILEGES ON `cantitatitadb`.* TO `cantina_user`@`localhost`
   ```
3. Si ves eso, el usuario fue creado correctamente ✅

---

## Paso 4: Probar Conexión

1. En MySQL Workbench, crea una nueva conexión
2. Usa estos datos:
   - **Connection Name:** Cantina User
   - **Hostname:** localhost
   - **Port:** 3306
   - **Username:** cantina_user
   - **Password:** L01G05S33Vice.42
3. Click en **Test Connection**
4. Debería decir "Successfully connected" ✅

---

## Paso 5: Actualizar .env.production

Después de crear el usuario, ejecuta esto en PowerShell:

```powershell
# Actualizar DB_USER en .env.production
(Get-Content entorno\.env.production) -replace 'DB_USER=root', 'DB_USER=cantina_user' | Set-Content entorno\.env.production
```

---

## Paso 6: Verificar

```powershell
python verificar_produccion.py
```

Debería dar ✅ **LISTO PARA PRODUCCIÓN**

---

## 🆘 Si tienes problemas

**Error: "Access denied for user 'cantina_user'@'localhost'"**
- Verifica que ejecutaste el FLUSH PRIVILEGES;
- Re-ejecuta todo el script SQL

**Error: "User 'cantina_user' already exists"**
- Ejecuta primero: `DROP USER 'cantina_user'@'localhost';`
- Luego ejecuta el CREATE USER nuevamente

**¿No tienes MySQL Workbench instalado?**
- Descarga desde: https://dev.mysql.com/downloads/workbench/
- O usa cualquier cliente MySQL (phpMyAdmin, DBeaver, etc.)

---

**Cuando termines de crear el usuario, avísame y actualizamos .env.production automáticamente**
