"""
Script para verificar índices de base de datos con EXPLAIN
Analiza las queries más críticas y verifica que estén usando índices correctamente
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from colorama import init, Fore, Style
import json

init()  # Inicializar colorama para colores en Windows

class AnalizadorIndices:
    """Analiza el uso de índices en queries críticas"""
    
    def __init__(self):
        self.resultados = []
        self.warnings = []
        self.errores = []
    
    def print_header(self, texto):
        """Imprime un encabezado formateado"""
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.WHITE}{texto}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    def analizar_query(self, nombre, query, tipo='SELECT'):
        """Analiza una query con EXPLAIN"""
        print(f"{Fore.YELLOW}📊 Analizando: {nombre}{Style.RESET_ALL}")
        print(f"   Query: {query[:100]}..." if len(query) > 100 else f"   Query: {query}")
        
        try:
            with connection.cursor() as cursor:
                # Ejecutar EXPLAIN
                cursor.execute(f"EXPLAIN {query}")
                explain_result = cursor.fetchall()
                
                # Analizar resultado
                usa_indice = False
                escaneo_completo = False
                rows_examinadas = 0
                
                for row in explain_result:
                    # Formato EXPLAIN: 
                    # [id, select_type, table, partitions, type, possible_keys, key, key_len, ref, rows, filtered, Extra]
                    tipo_acceso = row[4] if len(row) > 4 else None
                    key_usado = row[6] if len(row) > 6 else None
                    rows = row[9] if len(row) > 9 else 0
                    extra = row[11] if len(row) > 11 else ''
                    
                    rows_examinadas += rows if rows else 0
                    
                    # Verificar si usa índice
                    if key_usado and key_usado != 'NULL':
                        usa_indice = True
                    
                    # Verificar si hace table scan
                    if tipo_acceso == 'ALL':
                        escaneo_completo = True
                    
                    # Mostrar resultado
                    print(f"   {Fore.CYAN}Tabla: {row[2]}{Style.RESET_ALL}")
                    print(f"   Tipo: {tipo_acceso}")
                    print(f"   Índice usado: {key_usado if key_usado else 'NINGUNO'}")
                    print(f"   Filas examinadas: {rows:,}")
                    if extra:
                        print(f"   Extra: {extra}")
                
                # Evaluar resultado
                if not usa_indice and escaneo_completo:
                    print(f"   {Fore.RED}⚠️  WARNING: Escaneo completo de tabla sin índice{Style.RESET_ALL}")
                    self.warnings.append({
                        'nombre': nombre,
                        'problema': 'Escaneo completo sin índice',
                        'rows': rows_examinadas
                    })
                elif rows_examinadas > 10000:
                    print(f"   {Fore.YELLOW}⚠️  WARNING: Muchas filas examinadas ({rows_examinadas:,}){Style.RESET_ALL}")
                    self.warnings.append({
                        'nombre': nombre,
                        'problema': f'Examina {rows_examinadas:,} filas',
                        'rows': rows_examinadas
                    })
                elif usa_indice:
                    print(f"   {Fore.GREEN}✅ OK: Usando índice correctamente{Style.RESET_ALL}")
                else:
                    print(f"   {Fore.YELLOW}ℹ️  INFO: Query simple, puede no necesitar índice{Style.RESET_ALL}")
                
                self.resultados.append({
                    'nombre': nombre,
                    'usa_indice': usa_indice,
                    'rows': rows_examinadas,
                    'tipo_acceso': tipo_acceso,
                    'key': key_usado
                })
                
                print()
                
        except Exception as e:
            print(f"   {Fore.RED}❌ ERROR: {e}{Style.RESET_ALL}\n")
            self.errores.append({'nombre': nombre, 'error': str(e)})
    
    def verificar_indices_criticos(self):
        """Verifica las queries más críticas del sistema"""
        
        self.print_header("🔍 VERIFICACIÓN DE ÍNDICES - CANTINA TITA")
        
        # === QUERIES CRÍTICAS ===
        
        # 1. Búsqueda de productos por código de barras (POS)
        self.analizar_query(
            "Búsqueda producto por código barras",
            "SELECT * FROM productos WHERE Codigo_Barra = '7891234567890' LIMIT 1"
        )
        
        # 2. Búsqueda de tarjeta por número (POS)
        self.analizar_query(
            "Búsqueda tarjeta por número",
            "SELECT * FROM tarjetas WHERE Nro_Tarjeta = '12345678' LIMIT 1"
        )
        
        # 3. Ventas del día (Dashboard)
        self.analizar_query(
            "Ventas del día",
            f"SELECT COUNT(*), SUM(monto_total) FROM ventas WHERE DATE(fecha) = CURDATE()"
        )
        
        # 4. Productos más vendidos (Reportes)
        self.analizar_query(
            "Top productos vendidos",
            """SELECT p.descripcion, SUM(dv.cantidad) as total
               FROM detalle_venta dv
               JOIN productos p ON dv.id_producto = p.id_producto
               WHERE DATE(dv.id_venta) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
               GROUP BY p.id_producto
               ORDER BY total DESC
               LIMIT 10"""
        )
        
        # 5. Stock bajo (Alertas)
        self.analizar_query(
            "Productos con stock bajo",
            "SELECT * FROM stock_unico WHERE Stock_Actual <= Stock_Minimo"
        )
        
        # 6. Consumos de tarjeta del mes
        self.analizar_query(
            "Consumos tarjeta del mes",
            """SELECT ct.*, t.Nro_Tarjeta
               FROM consumos_tarjeta ct
               JOIN tarjetas t ON ct.Nro_Tarjeta = t.Nro_Tarjeta
               WHERE MONTH(ct.Fecha_Consumo) = MONTH(CURDATE())
               AND YEAR(ct.Fecha_Consumo) = YEAR(CURDATE())"""
        )
        
        # 7. Ventas por cajero (Auditoría)
        self.analizar_query(
            "Ventas por cajero",
            """SELECT e.nombre, COUNT(*) as total_ventas, SUM(v.monto_total) as total_monto
               FROM ventas v
               JOIN empleados e ON v.id_empleado_cajero = e.id_empleado
               WHERE DATE(v.fecha) = CURDATE()
               GROUP BY e.id_empleado"""
        )
        
        # 8. Recargas online pendientes
        self.analizar_query(
            "Recargas online pendientes",
            "SELECT * FROM transaccion_online WHERE Estado = 'PENDIENTE'"
        )
        
        # 9. Clientes activos con límite de crédito
        self.analizar_query(
            "Clientes activos con crédito",
            "SELECT * FROM clientes WHERE Activo = 1 AND Limite_Credito > 0 ORDER BY Limite_Credito DESC LIMIT 20"
        )
        
        # 10. Búsqueda de cliente por RUC/CI (Portal)
        self.analizar_query(
            "Búsqueda cliente por RUC/CI",
            "SELECT * FROM clientes WHERE Ruc_CI = '1234567' LIMIT 1"
        )
    
    def listar_indices_existentes(self):
        """Lista todos los índices creados en las tablas principales"""
        
        self.print_header("📋 ÍNDICES EXISTENTES EN LA BASE DE DATOS")
        
        tablas_principales = [
            'ventas', 'detalle_venta', 'productos', 'tarjetas',
            'consumo_tarjeta', 'stock_unico', 'clientes', 'empleados',
            'compras', 'transaccion_online'
        ]
        
        with connection.cursor() as cursor:
            for tabla in tablas_principales:
                try:
                    cursor.execute(f"SHOW INDEX FROM {tabla}")
                    indices = cursor.fetchall()
                    
                    print(f"{Fore.CYAN}📊 Tabla: {tabla}{Style.RESET_ALL}")
                    
                    indices_dict = {}
                    for idx in indices:
                        # Formato: Table, Non_unique, Key_name, Seq_in_index, Column_name, ...
                        key_name = idx[2]
                        column_name = idx[4]
                        
                        if key_name not in indices_dict:
                            indices_dict[key_name] = []
                        indices_dict[key_name].append(column_name)
                    
                    if indices_dict:
                        for key_name, columns in indices_dict.items():
                            tipo = "PK" if key_name == "PRIMARY" else "IDX"
                            print(f"   {tipo} {key_name}: {', '.join(columns)}")
                    else:
                        print(f"   {Fore.YELLOW}⚠️  Sin índices{Style.RESET_ALL}")
                    
                    print()
                    
                except Exception as e:
                    print(f"   {Fore.RED}❌ ERROR: {e}{Style.RESET_ALL}\n")
    
    def generar_reporte_final(self):
        """Genera un reporte final con recomendaciones"""
        
        self.print_header("📊 REPORTE FINAL")
        
        print(f"{Fore.WHITE}Total queries analizadas: {len(self.resultados)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Queries usando índices: {sum(1 for r in self.resultados if r['usa_indice'])}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Warnings: {len(self.warnings)}{Style.RESET_ALL}")
        print(f"{Fore.RED}Errores: {len(self.errores)}{Style.RESET_ALL}")
        print()
        
        if self.warnings:
            print(f"{Fore.YELLOW}⚠️  WARNINGS ENCONTRADOS:{Style.RESET_ALL}\n")
            for warning in self.warnings:
                print(f"   • {warning['nombre']}")
                print(f"     Problema: {warning['problema']}")
                print(f"     Filas: {warning['rows']:,}")
                print()
        
        if self.errores:
            print(f"{Fore.RED}❌ ERRORES ENCONTRADOS:{Style.RESET_ALL}\n")
            for error in self.errores:
                print(f"   • {error['nombre']}")
                print(f"     Error: {error['error']}")
                print()
        
        # Guardar reporte en JSON
        reporte = {
            'fecha': datetime.now().isoformat(),
            'total_queries': len(self.resultados),
            'con_indice': sum(1 for r in self.resultados if r['usa_indice']),
            'warnings': len(self.warnings),
            'errores': len(self.errores),
            'resultados': self.resultados,
            'warnings_detalle': self.warnings,
            'errores_detalle': self.errores
        }
        
        ruta_reporte = f"logs/verificacion_indices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('logs', exist_ok=True)
        
        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.CYAN}💾 Reporte guardado en: {ruta_reporte}{Style.RESET_ALL}")
        print()
        
        # Recomendaciones
        if self.warnings:
            print(f"{Fore.YELLOW}💡 RECOMENDACIONES:{Style.RESET_ALL}\n")
            print("   1. Revisa las queries con escaneos completos")
            print("   2. Considera agregar índices compuestos para queries complejas")
            print("   3. Analiza si las tablas necesitan mantenimiento (OPTIMIZE TABLE)")
            print("   4. Verifica estadísticas de las tablas (ANALYZE TABLE)")
            print()


def main():
    """Función principal"""
    try:
        analizador = AnalizadorIndices()
        
        # 1. Verificar queries críticas
        analizador.verificar_indices_criticos()
        
        # 2. Listar índices existentes
        analizador.listar_indices_existentes()
        
        # 3. Generar reporte final
        analizador.generar_reporte_final()
        
        print(f"{Fore.GREEN}✅ Análisis completado exitosamente{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}❌ ERROR FATAL: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
