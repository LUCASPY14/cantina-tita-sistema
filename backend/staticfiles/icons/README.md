# Íconos PWA para Cantina Tita POS

Este directorio debe contener los íconos de la aplicación web progresiva (PWA).

## Íconos Requeridos

Necesitas crear los siguientes archivos de imagen PNG con el logo de "Cantina Tita":

- `icon-16x16.png` - 16x16 píxeles (favicon pequeño)
- `icon-32x32.png` - 32x32 píxeles (favicon)
- `icon-72x72.png` - 72x72 píxeles (iOS)
- `icon-96x96.png` - 96x96 píxeles (Android)
- `icon-128x128.png` - 128x128 píxeles (Android)
- `icon-144x144.png` - 144x144 píxeles (Windows)
- `icon-152x152.png` - 152x152 píxeles (iOS iPad)
- `icon-192x192.png` - 192x192 píxeles (Android)
- `icon-384x384.png` - 384x384 píxeles (Android)
- `icon-512x512.png` - 512x512 píxeles (Android splash screen)

## Diseño Sugerido

El ícono debe incluir:
- 🏫 Emoji de escuela o 🍴 cubiertos
- Texto "TITA" o "CT" (Cantina Tita)
- Colores: Fondo naranja (#FF6B35) con texto blanco
- Borde redondeado (opcional)
- Diseño simple y legible en tamaños pequeños

## Herramientas para Generar Íconos

### Opción 1: PWA Asset Generator (Recomendado)
```bash
npm install -g pwa-asset-generator
pwa-asset-generator logo.svg ./static/icons
```

### Opción 2: Real Favicon Generator
1. Visita: https://realfavicongenerator.net/
2. Sube un logo de 512x512 píxeles
3. Descarga todos los tamaños generados
4. Copia los archivos a este directorio

### Opción 3: ImageMagick (línea de comandos)
```bash
# Crear todos los tamaños desde un logo original
convert logo.png -resize 16x16 icon-16x16.png
convert logo.png -resize 32x32 icon-32x32.png
convert logo.png -resize 72x72 icon-72x72.png
convert logo.png -resize 96x96 icon-96x96.png
convert logo.png -resize 128x128 icon-128x128.png
convert logo.png -resize 144x144 icon-144x144.png
convert logo.png -resize 152x152 icon-152x152.png
convert logo.png -resize 192x192 icon-192x192.png
convert logo.png -resize 384x384 icon-384x384.png
convert logo.png -resize 512x512 icon-512x512.png
```

### Opción 4: Favicon.io
1. Visita: https://favicon.io/favicon-generator/
2. Configura:
   - Texto: "CT" o "🏫"
   - Fondo: #FF6B35 (naranja)
   - Fuente: Bold, grande
3. Descarga y extrae los archivos
4. Copia a este directorio

## Logo de Ejemplo con Emoji (HTML/CSS)

Si no tienes un logo diseñado, puedes crear uno temporal con emojis:

```html
<div style="width: 512px; height: 512px; background: #FF6B35; display: flex; align-items: center; justify-content: center; border-radius: 100px;">
    <div style="text-align: center; color: white;">
        <div style="font-size: 200px; line-height: 1;">🏫</div>
        <div style="font-size: 80px; font-weight: bold; font-family: Arial;">TITA</div>
    </div>
</div>
```

Guarda esto como HTML, abre en navegador, captura screenshot y redimensiona.

## Verificación

Después de agregar los íconos:

1. Reinicia el servidor Django
2. Abre el POS en Chrome
3. Abre DevTools > Application > Manifest
4. Verifica que todos los íconos carguen correctamente
5. Prueba "Instalar aplicación" desde el menú del navegador

## Íconos Temporales

Si necesitas íconos temporales para pruebas, puedes:
1. Descargar íconos genéricos de: https://icons8.com/icons/set/school
2. Usar emojis convertidos a PNG: https://emoji.tools/
3. Crear íconos de texto con: https://favicon.io/favicon-generator/

## Nota

Los íconos con formato "maskable" funcionan mejor en Android adaptativo.
Para mejores resultados, deja 10% de margen alrededor del diseño principal.
