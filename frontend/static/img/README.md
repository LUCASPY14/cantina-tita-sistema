# Logotipo de Cantina Tita

## Ubicación del Logotipo

Coloca tu logotipo en esta carpeta con el nombre: **`logo.png`**

## Especificaciones Recomendadas

### Formato
- **Formato preferido:** PNG con fondo transparente
- **Alternativas aceptables:** JPG, SVG

### Tamaño
- **Tamaño óptimo:** 400x400 píxeles o 512x512 píxeles
- **Relación de aspecto:** Cuadrado (1:1) o ligeramente horizontal
- **Peso máximo:** Menor a 500KB para óptima velocidad de carga

### Calidad
- **Resolución mínima:** 300 DPI para calidad profesional
- **Colores:** RGB (para web)
- **Fondo:** Transparente (PNG) para versatilidad

## Variantes Opcionales

Puedes agregar variantes del logotipo para diferentes contextos:

1. **`logo.png`** - Logotipo principal (obligatorio)
2. **`logo-horizontal.png`** - Versión horizontal (opcional)
3. **`logo-white.png`** - Versión en blanco para fondos oscuros (opcional)
4. **`logo-icon.png`** - Solo el icono sin texto (opcional)
5. **`favicon.ico`** - Favicon para el navegador (16x16, 32x32, 48x48)

## Cómo Agregar tu Logotipo

### Opción 1: Copiar manualmente
```
1. Abre esta carpeta en el explorador de archivos
2. Copia tu archivo de logotipo
3. Renómbralo como "logo.png"
```

### Opción 2: Desde la terminal
```powershell
# Copia tu logotipo desde su ubicación actual
Copy-Item "C:\ruta\a\tu\logo.png" "D:\anteproyecto20112025\static\img\logo.png"
```

### Opción 3: Arrastrar y soltar
```
1. Abre VS Code
2. Arrastra tu archivo de logotipo a esta carpeta
3. Renómbralo como "logo.png"
```

## Uso en el Sistema

El logotipo se utiliza en:

✅ **Página de login** - Tamaño grande, centrado  
✅ **Barra de navegación** - Tamaño pequeño (32x32 auto-escalado)  
✅ **Reportes impresos** - Encabezado de documentos  
✅ **Tickets de venta** - Pie de comprobante  
✅ **Correos electrónicos** - Firma corporativa  

## Fallback (Respaldo)

Si no colocas un logotipo personalizado, el sistema usará:
- El icono por defecto ubicado en `static/icons/icon-512.png`
- Un placeholder con el texto "Cantina Tita"

## Prueba tu Logotipo

Después de agregar el logotipo, verifica que se muestre correctamente:

1. Inicia el servidor: `python manage.py runserver`
2. Abre tu navegador en: `http://localhost:8000/login/`
3. Verifica que el logotipo se muestre correctamente

## Soporte

Si el logotipo no se muestra:
- Verifica que el archivo se llame exactamente `logo.png`
- Confirma que esté en la carpeta correcta: `static/img/`
- Asegúrate de que Django haya detectado el archivo (reinicia el servidor)
- Verifica los permisos de lectura del archivo

## Optimización

Para optimizar tu logotipo:

### Herramientas online gratuitas:
- **TinyPNG:** https://tinypng.com/ (reduce tamaño sin perder calidad)
- **Remove.bg:** https://www.remove.bg/ (quita el fondo)
- **Canva:** https://www.canva.com/ (edita y ajusta dimensiones)

### Herramientas de línea de comandos:
```powershell
# Usando ImageMagick (si está instalado)
magick convert logo-original.png -resize 512x512 -background none logo.png
```

## Información Adicional

- El sistema usa lazy loading para el logotipo
- Se incluye un `onerror` para mostrar un fallback automático
- El logotipo tiene animación de "float" en la página de login
- Es responsive y se adapta a dispositivos móviles

---

**Última actualización:** 27 de Noviembre 2025  
**Sistema:** Cantina Tita v1.0
