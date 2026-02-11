"""
Script para generar DER (Físico y Lógico) por MÓDULOS FUNCIONALES
Organiza las 101 tablas de cantinatitadb en módulos exhaustivos
Genera DER Lógico y Físico para cada módulo

Características:
- TODAS las tablas están asignadas a algún módulo
- Genera 2 diagramas por módulo (Lógico + Físico)
- Diagramas individuales más manejables y claros
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from decouple import config
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import graphviz

# Configuración de la base de datos
DB_CONFIG = {
    'host': config('DB_HOST', default='localhost'),
    'port': config('DB_PORT', default='3306'),
    'user': config('DB_USER', default='root'),
    'password': config('DB_PASSWORD'),
    'database': config('DB_NAME', default='cantinatitadb'),
}

# Organización EXHAUSTIVA de las 101 tablas en módulos funcionales
MODULES = {
    '01_Autenticacion_Django': {
        'description': 'Sistema de autenticación y permisos de Django',
        'tables': [
            'auth_user', 'auth_group', 'auth_permission',
            'auth_group_permissions', 'auth_user_groups', 'auth_user_user_permissions',
            'django_admin_log', 'django_content_type', 'django_migrations', 'django_session'
        ],
        'color': '#E3F2FD',
        'border': '#1976D2'
    },
    '02_Clientes_Padres': {
        'description': 'Gestión de clientes y padres de familia',
        'tables': [
            'clientes', 'tipos_cliente', 'usuarios_portal', 'usuario_portal',
            'usuarios_web_clientes', 'preferencia_notificacion'
        ],
        'color': '#F3E5F5',
        'border': '#7B1FA2'
    },
    '03_Hijos_Estudiantes': {
        'description': 'Gestión de hijos/estudiantes y educación',
        'tables': [
            'hijos', 'grados', 'historial_grados_hijos',
            'restricciones_hijos', 'restricciones_horarias'
        ],
        'color': '#E8F5E9',
        'border': '#388E3C'
    },
    '04_Tarjetas_Saldo': {
        'description': 'Tarjetas, saldo y autorizaciones',
        'tables': [
            'tarjetas', 'tarjetas_autorizacion', 'cargas_saldo',
            'consumos_tarjeta', 'autorizacion_saldo_negativo',
            'aceptacion_terminos_saldo_negativo', 'log_autorizaciones',
            'notificacion_saldo', 'bloqueos_cuenta'
        ],
        'color': '#FFF3E0',
        'border': '#F57C00'
    },
    '05_Productos_Catalogo': {
        'description': 'Catálogo de productos, categorías y alergenos',
        'tables': [
            'productos', 'categorias', 'unidades_medida',
            'alergenos', 'producto_alergenos'
        ],
        'color': '#FCE4EC',
        'border': '#C2185B'
    },
    '06_Inventario_Stock': {
        'description': 'Control de inventario y movimientos de stock',
        'tables': [
            'stock_unico', 'movimientos_stock', 'ajustes_inventario',
            'detalle_ajuste', 'costos_historicos', 'historico_precios'
        ],
        'color': '#E0F2F1',
        'border': '#00796B'
    },
    '07_Precios_Impuestos': {
        'description': 'Gestión de precios, listas e impuestos',
        'tables': [
            'listas_precios', 'precios_por_lista', 'impuestos'
        ],
        'color': '#F1F8E9',
        'border': '#689F38'
    },
    '08_Ventas_POS': {
        'description': 'Ventas en punto de venta',
        'tables': [
            'ventas', 'detalle_venta', 'medios_pago', 'tipos_pago'
        ],
        'color': '#FFF9C4',
        'border': '#F9A825'
    },
    '09_Pagos_Ventas': {
        'description': 'Pagos relacionados con ventas',
        'tables': [
            'pagos_venta', 'aplicacion_pagos_ventas',
            'transaccion_online', 'conciliacion_pagos'
        ],
        'color': '#E1F5FE',
        'border': '#0277BD'
    },
    '10_Compras_Proveedores': {
        'description': 'Compras y gestión de proveedores',
        'tables': [
            'compras', 'detalle_compra', 'proveedores',
            'pagos_proveedores', 'aplicacion_pagos_compras'
        ],
        'color': '#F8BBD0',
        'border': '#AD1457'
    },
    '11_Notas_Credito': {
        'description': 'Notas de crédito a clientes y proveedores',
        'tables': [
            'notas_credito_cliente', 'detalle_nota',
            'notas_credito_proveedor', 'detalle_nota_credito_proveedor'
        ],
        'color': '#E8EAF6',
        'border': '#3F51B5'
    },
    '12_Promociones': {
        'description': 'Sistema de promociones y descuentos',
        'tables': [
            'promociones', 'promociones_aplicadas',
            'productos_promocion', 'categorias_promocion'
        ],
        'color': '#FFEBEE',
        'border': '#D32F2F'
    },
    '13_Almuerzo_Planes': {
        'description': 'Planes y tipos de almuerzo escolar',
        'tables': [
            'planes_almuerzo', 'tipos_almuerzo', 'suscripciones_almuerzo',
            'registro_consumo_almuerzo', 'cuentas_almuerzo_mensual',
            'pagos_cuentas_almuerzo', 'pagos_almuerzo_mensual'
        ],
        'color': '#E0F7FA',
        'border': '#00ACC1'
    },
    '14_Empleados_RRHH': {
        'description': 'Empleados y recursos humanos',
        'tables': [
            'empleados', 'tipos_rol_general', 'tarifas_comision'
        ],
        'color': '#FBE9E7',
        'border': '#D84315'
    },
    '15_Comisiones': {
        'description': 'Comisiones de empleados',
        'tables': [
            'detalle_comision_venta', 'auditoria_comisiones'
        ],
        'color': '#F3E5F5',
        'border': '#8E24AA'
    },
    '16_Cajas_Cierres': {
        'description': 'Cajas y cierres de caja',
        'tables': [
            'cajas', 'cierres_caja'
        ],
        'color': '#FFFDE7',
        'border': '#FBC02D'
    },
    '17_Facturacion': {
        'description': 'Facturación electrónica y física',
        'tables': [
            'datos_facturacion_elect', 'datos_facturacion_fisica',
            'timbrados', 'puntos_expedicion', 'documentos_tributarios',
            'datos_empresa'
        ],
        'color': '#E8F5E9',
        'border': '#43A047'
    },
    '18_Seguridad_2FA': {
        'description': 'Seguridad, autenticación 2FA y sesiones',
        'tables': [
            'autenticacion_2fa', 'intentos_2fa', 'intentos_login',
            'sesiones_activas', 'renovaciones_sesion', 'patrones_acceso'
        ],
        'color': '#FFEBEE',
        'border': '#E53935'
    },
    '19_Tokens_Verificacion': {
        'description': 'Tokens de verificación y recuperación',
        'tables': [
            'token_verificacion', 'tokens_verificacion',
            'tokens_recuperacion'
        ],
        'color': '#F3E5F5',
        'border': '#AB47BC'
    },
    '20_Notificaciones': {
        'description': 'Sistema de notificaciones',
        'tables': [
            'notificacion', 'solicitudes_notificacion'
        ],
        'color': '#E1F5FE',
        'border': '#039BE5'
    },
    '21_Alertas_Anomalias': {
        'description': 'Alertas y detección de anomalías',
        'tables': [
            'alertas_sistema', 'anomalias_detectadas'
        ],
        'color': '#FFF3E0',
        'border': '#FB8C00'
    },
    '22_Auditoria': {
        'description': 'Auditoría y trazabilidad',
        'tables': [
            'auditoria_operaciones', 'auditoria_empleados',
            'auditoria_usuarios_web'
        ],
        'color': '#ECEFF1',
        'border': '#546E7A'
    }
}

# Colores para los diagramas
COLORS = {
    'pk_bg': '#FFE5B4',
    'fk_bg': '#C8E6C9',
    'attribute_bg': '#FFFFFF',
    'relation_color': '#FF6B35',
}


class DERModulosGenerator:
    """Generador de DER por módulos funcionales"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.engine = None
        self.metadata = None
        self.inspector = None
        self.output_dir = Path('diagramas_der_modulos')
        self.output_dir.mkdir(exist_ok=True)
        
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            )
            self.engine = create_engine(connection_string)
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            self.inspector = inspect(self.engine)
            print(f"✓ Conexión exitosa a '{self.db_config['database']}'")
            return True
        except SQLAlchemyError as e:
            print(f"✗ Error al conectar: {e}")
            return False
    
    def get_table_info(self, table_name):
        """Obtiene información detallada de una tabla"""
        try:
            columns = self.inspector.get_columns(table_name)
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            pk_columns = pk_constraint.get('constrained_columns', [])
            
            return {
                'columns': columns,
                'primary_keys': pk_columns,
                'foreign_keys': foreign_keys
            }
        except Exception as e:
            return None
    
    def format_column_type(self, column_type):
        """Formatea el tipo de columna"""
        return str(column_type)[:30]
    
    def generate_logical_der_module(self, module_name, module_info):
        """Genera DER Lógico para un módulo específico"""
        existing_tables = set(self.inspector.get_table_names())
        tables_in_module = [t for t in module_info['tables'] if t in existing_tables]
        
        if not tables_in_module:
            return None
        
        print(f"\n  Generando DER Lógico: {module_name}")
        
        dot = graphviz.Digraph(
            name=f'DER_Logico_{module_name}',
            comment=f'DER Lógico - {module_info["description"]}',
            format='png',
            engine='dot'
        )
        
        # Configuración
        dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.0')
        dot.attr('node', shape='plaintext', fontname='Arial', fontsize='10')
        dot.attr('edge', color=COLORS['relation_color'], fontname='Arial', 
                fontsize='9', penwidth='2')
        
        # Título
        dot.attr(label=f'{module_info["description"]}\nDER LÓGICO\n'
                      f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                fontsize='14', fontname='Arial Bold', labelloc='t')
        
        # Crear nodos
        for table in sorted(tables_in_module):
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            label = f'''<
                <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    <TR><TD BGCOLOR="{module_info['border']}" COLSPAN="2">
                        <FONT COLOR="white" POINT-SIZE="11"><B>{table.upper()}</B></FONT>
                    </TD></TR>
            '''
            
            # PKs
            for col in table_info['columns']:
                if col['name'] in table_info['primary_keys']:
                    label += f'''<TR>
                        <TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT"><B>🔑 {col['name']}</B></TD>
                        <TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT">PK</TD>
                    </TR>'''
            
            # FKs
            fk_columns = []
            for fk in table_info['foreign_keys']:
                if fk['constrained_columns']:
                    fk_columns.extend(fk['constrained_columns'])
            
            for col in table_info['columns']:
                if col['name'] in fk_columns and col['name'] not in table_info['primary_keys']:
                    label += f'''<TR>
                        <TD BGCOLOR="{COLORS['fk_bg']}" ALIGN="LEFT">🔗 {col['name']}</TD>
                        <TD BGCOLOR="{COLORS['fk_bg']}" ALIGN="LEFT">FK</TD>
                    </TR>'''
            
            # Atributos importantes
            count = 0
            for col in table_info['columns']:
                if (col['name'] not in table_info['primary_keys'] and 
                    col['name'] not in fk_columns and count < 5):
                    if any(kw in col['name'].lower() for kw in 
                          ['nombre', 'fecha', 'monto', 'total', 'estado', 'activo', 'tipo']):
                        label += f'''<TR>
                            <TD BGCOLOR="{COLORS['attribute_bg']}" ALIGN="LEFT" COLSPAN="2">
                                {col['name']}
                            </TD>
                        </TR>'''
                        count += 1
            
            label += '</TABLE>>'
            dot.node(table, label=label)
        
        # Relaciones
        for table in tables_in_module:
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                if ref_table in tables_in_module:
                    label = fk['constrained_columns'][0] if fk['constrained_columns'] else ''
                    dot.edge(table, ref_table, label=label, arrowhead='crow')
        
        # Guardar
        safe_name = module_name.replace(' ', '_').replace('/', '_')
        output_path = self.output_dir / f'{safe_name}_Logico'
        dot.render(output_path, cleanup=True)
        print(f"    ✓ {output_path}.png")
        return str(output_path) + '.png'
    
    def generate_physical_der_module(self, module_name, module_info):
        """Genera DER Físico para un módulo específico"""
        existing_tables = set(self.inspector.get_table_names())
        tables_in_module = [t for t in module_info['tables'] if t in existing_tables]
        
        if not tables_in_module:
            return None
        
        print(f"  Generando DER Físico: {module_name}")
        
        dot = graphviz.Digraph(
            name=f'DER_Fisico_{module_name}',
            comment=f'DER Físico - {module_info["description"]}',
            format='png',
            engine='dot'
        )
        
        # Configuración
        dot.attr(rankdir='TB', splines='polyline', nodesep='0.8', ranksep='1.2')
        dot.attr('node', shape='plaintext', fontname='Courier', fontsize='9')
        dot.attr('edge', color=COLORS['relation_color'], fontname='Arial', 
                fontsize='8', penwidth='1.5')
        
        # Título
        dot.attr(label=f'{module_info["description"]}\nDER FÍSICO\n'
                      f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                fontsize='14', fontname='Arial Bold', labelloc='t')
        
        # Crear nodos detallados
        for table in sorted(tables_in_module):
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            label = f'''<
                <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3">
                    <TR><TD BGCOLOR="{module_info['border']}" COLSPAN="4">
                        <FONT COLOR="white" POINT-SIZE="11"><B>{table}</B></FONT>
                    </TD></TR>
                    <TR>
                        <TD BGCOLOR="#D3D3D3"><B>Column</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Type</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Null</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Key</B></TD>
                    </TR>
            '''
            
            # Todas las columnas
            for col in table_info['columns']:
                col_name = col['name']
                col_type = self.format_column_type(col['type'])
                nullable = 'YES' if col['nullable'] else 'NO'
                
                key_type = ''
                bgcolor = COLORS['attribute_bg']
                
                if col_name in table_info['primary_keys']:
                    key_type = 'PK'
                    bgcolor = COLORS['pk_bg']
                
                for fk in table_info['foreign_keys']:
                    if fk['constrained_columns'] and col_name in fk['constrained_columns']:
                        key_type = 'PK,FK' if key_type else 'FK'
                        bgcolor = COLORS['fk_bg']
                
                key_display = f'<B>{key_type}</B>' if key_type else ''
                
                label += f'''<TR>
                    <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_name}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_type}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="CENTER">{nullable}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="CENTER">{key_display}</TD>
                </TR>'''
            
            label += '</TABLE>>'
            dot.node(table, label=label)
        
        # Relaciones
        for table in tables_in_module:
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                if ref_table in tables_in_module and fk['constrained_columns'] and fk['referred_columns']:
                    label = f"{fk['constrained_columns'][0]}\n→\n{fk['referred_columns'][0]}"
                    dot.edge(table, ref_table, label=label, arrowhead='normal', arrowtail='crow', dir='both')
        
        # Guardar
        safe_name = module_name.replace(' ', '_').replace('/', '_')
        output_path = self.output_dir / f'{safe_name}_Fisico'
        dot.render(output_path, cleanup=True)
        print(f"    ✓ {output_path}.png")
        return str(output_path) + '.png'
    
    def generate_all_modules(self):
        """Genera DER Lógico y Físico para todos los módulos"""
        print("\n" + "="*70)
        print("GENERANDO DER POR MÓDULOS (LÓGICO + FÍSICO)")
        print("="*70)
        
        total_tables_assigned = set()
        generated_files = []
        
        for module_name, module_info in MODULES.items():
            print(f"\n📁 Módulo: {module_name}")
            print(f"   {module_info['description']}")
            print(f"   Tablas: {len(module_info['tables'])}")
            
            total_tables_assigned.update(module_info['tables'])
            
            # Generar DER Lógico
            logical_file = self.generate_logical_der_module(module_name, module_info)
            if logical_file:
                generated_files.append(logical_file)
            
            # Generar DER Físico
            physical_file = self.generate_physical_der_module(module_name, module_info)
            if physical_file:
                generated_files.append(physical_file)
        
        return generated_files, total_tables_assigned
    
    def verify_coverage(self):
        """Verifica que todas las tablas estén asignadas"""
        print("\n" + "="*70)
        print("VERIFICACIÓN DE COBERTURA")
        print("="*70)
        
        all_tables = set(self.inspector.get_table_names())
        assigned_tables = set()
        
        for module_info in MODULES.values():
            assigned_tables.update(module_info['tables'])
        
        missing_tables = all_tables - assigned_tables
        extra_tables = assigned_tables - all_tables
        
        print(f"\nTablas en BD: {len(all_tables)}")
        print(f"Tablas asignadas: {len(assigned_tables)}")
        print(f"Cobertura: {len(assigned_tables)/len(all_tables)*100:.1f}%")
        
        if missing_tables:
            print(f"\n⚠ TABLAS NO ASIGNADAS ({len(missing_tables)}):")
            for table in sorted(missing_tables):
                print(f"  - {table}")
        else:
            print("\n✓ TODAS las tablas están asignadas a módulos")
        
        if extra_tables:
            print(f"\n⚠ TABLAS ASIGNADAS QUE NO EXISTEN ({len(extra_tables)}):")
            for table in sorted(extra_tables):
                print(f"  - {table}")
        
        return len(missing_tables) == 0
    
    def generate_index_html(self, generated_files):
        """Genera índice HTML con todos los diagramas"""
        print("\n" + "="*70)
        print("GENERANDO ÍNDICE HTML")
        print("="*70)
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DER por Módulos - CantinatitaDB</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .module {{
            margin-bottom: 50px;
            border: 2px solid #ddd;
            border-radius: 10px;
            overflow: hidden;
        }}
        .module-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 2px solid #ddd;
        }}
        .module-header h2 {{ color: #1e3c72; margin-bottom: 5px; }}
        .module-header p {{ color: #666; font-size: 0.95em; }}
        .diagrams {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; }}
        .diagram {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }}
        .diagram h3 {{ color: #2a5298; margin-bottom: 10px; font-size: 1.1em; }}
        .diagram img {{ width: 100%; border-radius: 5px; cursor: pointer; }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            padding: 20px;
        }}
        .modal-content {{ margin: auto; max-width: 95%; max-height: 95%; }}
        .modal-content img {{ max-width: 100%; max-height: 90vh; border-radius: 8px; }}
        .close {{
            position: absolute;
            top: 20px;
            right: 40px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .footer {{ background: #f8f9fa; padding: 30px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DER por Módulos Funcionales</h1>
            <h2>Base de Datos: {self.db_config['database']}</h2>
            <p>Generado: {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            <p>Total: {len(MODULES)} módulos | {len(generated_files)} diagramas</p>
        </div>
        <div class="content">
"""
        
        for module_name, module_info in MODULES.items():
            safe_name = module_name.replace(' ', '_').replace('/', '_')
            
            html_content += f"""
            <div class="module">
                <div class="module-header">
                    <h2>{module_name}</h2>
                    <p>{module_info['description']}</p>
                    <p><strong>Tablas ({len(module_info['tables'])}):</strong> {', '.join(module_info['tables'])}</p>
                </div>
                <div class="diagrams">
                    <div class="diagram">
                        <h3>🔍 DER Lógico</h3>
                        <img src="{safe_name}_Logico.png" alt="DER Lógico" onclick="openModal(this.src)">
                    </div>
                    <div class="diagram">
                        <h3>⚙️ DER Físico</h3>
                        <img src="{safe_name}_Fisico.png" alt="DER Físico" onclick="openModal(this.src)">
                    </div>
                </div>
            </div>
"""
        
        html_content += f"""
        </div>
        <div class="footer">
            <p><strong>Sistema de Gestión de Cantina Escolar - Cantina Tita</strong></p>
            <p>Diagramas generados automáticamente con Python, SQLAlchemy y Graphviz</p>
            <p>© {datetime.now().year}</p>
        </div>
    </div>
    
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="">
        </div>
    </div>
    
    <script>
        function openModal(src) {{
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = src;
        }}
        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>
"""
        
        html_file = self.output_dir / 'index_modulos.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Índice HTML generado: {html_file}")
        return str(html_file)
    
    def close(self):
        """Cierra la conexión"""
        if self.engine:
            self.engine.dispose()


def main():
    """Función principal"""
    print("="*70)
    print("GENERADOR DE DER POR MÓDULOS - CANTINATITADB")
    print("="*70)
    
    generator = DERModulosGenerator(DB_CONFIG)
    
    if not generator.connect():
        sys.exit(1)
    
    try:
        # Verificar cobertura
        all_covered = generator.verify_coverage()
        
        if not all_covered:
            print("\n⚠ ADVERTENCIA: No todas las tablas están asignadas")
            response = input("¿Desea continuar de todos modos? (s/n): ")
            if response.lower() != 's':
                sys.exit(0)
        
        # Generar DER por módulos
        generated_files, total_assigned = generator.generate_all_modules()
        
        # Generar índice HTML
        html_file = generator.generate_index_html(generated_files)
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO")
        print("="*70)
        print(f"\nMódulos procesados: {len(MODULES)}")
        print(f"Tablas asignadas: {len(total_assigned)}")
        print(f"Diagramas generados: {len(generated_files)}")
        print(f"\nArchivos en: {generator.output_dir.absolute()}")
        print(f"Índice HTML: {html_file}")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        generator.close()


if __name__ == '__main__':
    main()
