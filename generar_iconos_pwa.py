"""
Generador de iconos PWA en múltiples tamaños
Genera iconos desde 72x72 hasta 512x512 para Progressive Web App
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Crear un icono con el logo de Cantina Tita"""
    
    # Crear imagen con fondo del color principal
    img = Image.new('RGB', (size, size), '#FF6B35')
    draw = ImageDraw.Draw(img)
    
    # Crear círculo blanco en el centro
    margin = size // 8
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill='white')
    
    # Agregar texto "CT" (Cantina Tita)
    try:
        # Intentar usar una fuente del sistema
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback a fuente por defecto
        font = ImageFont.load_default()
    
    # Texto centrado
    text = "CT"
    
    # Obtener dimensiones del texto para centrarlo
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Posición centrada
    x = (size - text_width) / 2
    y = (size - text_height) / 2 - size // 20  # Ajuste fino vertical
    
    # Dibujar texto en naranja
    draw.text((x, y), text, fill='#FF6B35', font=font)
    
    # Guardar
    img.save(output_path, 'PNG', optimize=True)
    print(f'✓ Creado: {output_path} ({size}x{size})')

def generate_pwa_icons():
    """Generar todos los iconos necesarios para PWA"""
    
    # Directorio de salida
    icons_dir = os.path.join('frontend', 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamaños requeridos para PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print('\n🎨 Generando iconos PWA...\n')
    
    for size in sizes:
        filename = f'icon-{size}x{size}.png'
        output_path = os.path.join(icons_dir, filename)
        
        # Solo crear si no existe
        if not os.path.exists(output_path):
            create_icon(size, output_path)
        else:
            print(f'⏭️  Ya existe: {filename}')
    
    print('\n✅ Iconos PWA generados exitosamente!\n')

if __name__ == '__main__':
    generate_pwa_icons()
