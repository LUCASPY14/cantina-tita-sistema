import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_FILE = BASE_DIR / "gestion" / "models.py"

def analyze_models():
    """Analiza models.py para encontrar problemas"""
    print("🔍 ANALIZANDO models.py...")
    if not MODELS_FILE.exists():
        print(f"❌ No se encontró: {MODELS_FILE}")
        return False
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    model_pattern = r'class\s+(\w+)\(.*models\.Model.*\):'
    models = re.findall(model_pattern, content)
    print(f"✅ Modelos encontrados en gestion/models.py: {len(models)}")
    print("   " + ", ".join(models))
    missing_models = []
    fk_pattern = r'ForeignKey\(\s*["\']?(\w+)["\']?\s*,'
    fk_matches = re.findall(fk_pattern, content)
    model_references = [m for m in fk_matches if m[0].isupper()]
    print(f"\n🔍 Referencias ForeignKey encontradas: {len(model_references)}")
    for ref in model_references:
        if ref not in models:
            missing_models.append(ref)
    if missing_models:
        print(f"\n❌ MODELOS INEXISTENTES REFERENCIADOS: {len(missing_models)}")
        for model in missing_models:
            print(f"   - {model}")
        return missing_models
    else:
        print("\n✅ Todas las referencias ForeignKey apuntan a modelos existentes")
        return []

def fix_detallecompra():
    """Corrige DetalleCompra.compra ForeignKey"""
    print("\n🔧 CORRIGIENDO DetalleCompra.compra...")
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    in_detallecompra = False
    compra_field_found = False
    for i, line in enumerate(lines):
        if 'class DetalleCompra' in line:
            in_detallecompra = True
            print(f"✅ DetalleCompra encontrado en línea {i+1}")
        if in_detallecompra and 'compra' in line and 'ForeignKey' in line:
            print(f"⚠️  Campo problemático encontrado en línea {i+1}:")
            print(f"   {line.strip()}")
            lines[i] = f"# {line.strip()}  # COMENTADO: Modelo CompraProveedor no existe\n"
            print("✅ Campo comentado")
            compra_field_found = True
        if in_detallecompra and line.strip() == '' and i > 0 and 'class ' in lines[i-1]:
            in_detallecompra = False
    if not compra_field_found:
        print("⚠️  No se encontró campo 'compra' en DetalleCompra")
    with open(MODELS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return compra_field_found

def fix_detalleventa():
    """Corrige DetalleVenta.venta ForeignKey"""
    print("\n🔧 CORRIGIENDO DetalleVenta.venta...")
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    in_detalleventa = False
    venta_field_found = False
    for i, line in enumerate(lines):
        if 'class DetalleVenta' in line:
            in_detalleventa = True
            print(f"✅ DetalleVenta encontrado en línea {i+1}")
        if in_detalleventa and 'venta' in line and 'ForeignKey' in line:
            print(f"⚠️  Campo problemático encontrado en línea {i+1}:")
            print(f"   {line.strip()}")
            lines[i] = f"# {line.strip()}  # COMENTADO: Modelo Venta no existe en gestion\n"
            print("✅ Campo comentado")
            venta_field_found = True
        if in_detalleventa and line.strip() == '' and i > 0 and 'class ' in lines[i-1]:
            in_detalleventa = False
    if not venta_field_found:
        print("⚠️  No se encontró campo 'venta' en DetalleVenta")
    with open(MODELS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return venta_field_found

def main():
    print("=== CORRIGIENDO REFERENCIAS A MODELOS INEXISTENTES ===")
    missing = analyze_models()
    if not missing:
        print("\n✅ No hay problemas encontrados")
        return
    print("\n" + "="*50)
    fix_detallecompra()
    print("\n" + "="*50)
    fix_detalleventa()
    print("\n" + "="*50)
    print("✅ CORRECCIONES APLICADAS")
    print("="*50)
    print("""
📋 PRÓXIMOS PASOS:

1. ✅ Modelos corregidos en gestion/models.py
2. 🔧 Ahora ejecuta:
   python manage.py makemigrations gestion
   python manage.py migrate gestion
   
3. 🔍 Si hay más errores, repite el proceso

⚠️  NOTA: Si los modelos Venta/Compra deberían estar en otra app (ej: 'pos'),
    considera moverlos o usar app_label en el ForeignKey.
""")

if __name__ == '__main__':
    main()
