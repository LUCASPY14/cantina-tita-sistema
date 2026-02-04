"""
Script para generar DER Modular de la base de datos 'cantinatitadb'
Agrupa las tablas por módulos funcionales para mejor visualización

Módulos:
- Gestión de Clientes y Padres
- Gestión de Hijos/Estudiantes
- Gestión de Productos e Inventario
- Gestión de Ventas y Transacciones
- Gestión de Empleados y Seguridad
- Configuración y Catálogos
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

# Agrupación de tablas por módulos funcionales
MODULES = {
    'Clientes y Padres': {
        'tables': ['clientes', 'tipos_cliente', 'padres', 'auth_user'],
        'color': '#E3F2FD',
        'border': '#1976D2'
    },
    'Hijos/Estudiantes': {
        'tables': ['hijos', 'grados', 'secciones', 'restricciones_hijo', 'autorizaciones_compra'],
        'color': '#F3E5F5',
        'border': '#7B1FA2'
    },
    'Productos e Inventario': {
        'tables': ['productos', 'categorias', 'unidades_medida', 'inventario', 
                   'movimientos_inventario', 'componentes_almuerzo', 'stock_diario'],
        'color': '#FFF3E0',
        'border': '#E65100'
    },
    'Ventas y Transacciones': {
        'tables': ['ventas', 'detalles_ventas', 'medios_pago', 'transacciones_pago',
                   'transacciones_metrepay', 'historial_recargas'],
        'color': '#E8F5E9',
        'border': '#2E7D32'
    },
    'Empleados y Seguridad': {
        'tables': ['empleados', 'roles', 'permisos', 'roles_permisos', 'sesiones_2fa',
                   'tokens_autenticacion', 'auditoria_accesos', 'intentos_login'],
        'color': '#FFEBEE',
        'border': '#C62828'
    },
    'Reportes y Comisiones': {
        'tables': ['reportes_ventas', 'comisiones'],
        'color': '#FCE4EC',
        'border': '#AD1457'
    },
    'Configuración': {
        'tables': ['listas_precios', 'precios_productos', 'impuestos', 'configuracion_sistema',
                   'horarios_operacion', 'parametros_seguridad'],
        'color': '#F1F8E9',
        'border': '#558B2F'
    }
}

# Colores
COLORS = {
    'pk_bg': '#FFE5B4',
    'fk_bg': '#C8E6C9',
    'attribute_bg': '#FFFFFF',
    'relation_color': '#FF6B35',
}


class ModularDERGenerator:
    """Generador de DER Modular"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.engine = None
        self.metadata = None
        self.inspector = None
        self.output_dir = Path('diagramas_der')
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
    
    def generate_modular_der(self):
        """Genera DER agrupado por módulos funcionales"""
        print("\n" + "="*70)
        print("GENERANDO DER MODULAR POR MÓDULOS FUNCIONALES")
        print("="*70)
        
        dot = graphviz.Digraph(
            name='DER_Modular_CantinatitaDB',
            comment='DER Modular - Agrupado por Módulos Funcionales',
            format='png',
            engine='dot'
        )
        
        # Configuración general
        dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='1.0',
                compound='true', concentrate='true')
        dot.attr('node', shape='plaintext', fontname='Arial', fontsize='9')
        dot.attr('edge', color=COLORS['relation_color'], fontname='Arial', 
                fontsize='8', penwidth='1.5')
        
        # Título
        dot.attr(label=f'DER MODULAR - {self.db_config["database"]}\n'
                      f'Agrupado por Módulos Funcionales\n'
                      f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                fontsize='16', fontname='Arial Bold', labelloc='t')
        
        # Obtener todas las tablas existentes
        existing_tables = set(self.inspector.get_table_names())
        all_foreign_keys = []
        
        # Crear subgrafos para cada módulo
        for module_name, module_info in MODULES.items():
            with dot.subgraph(name=f'cluster_{module_name.replace(" ", "_")}') as subgraph:
                subgraph.attr(label=module_name, style='filled,rounded',
                            fillcolor=module_info['color'],
                            color=module_info['border'],
                            penwidth='2',
                            fontname='Arial Bold',
                            fontsize='12')
                
                # Agregar tablas del módulo que existen en la BD
                tables_in_module = [t for t in module_info['tables'] if t in existing_tables]
                
                for table in tables_in_module:
                    table_info = self.get_table_info(table)
                    if not table_info:
                        continue
                    
                    # Crear nodo de tabla
                    label = f'''<
                        <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3">
                            <TR><TD BGCOLOR="{module_info['border']}" COLSPAN="2">
                                <FONT COLOR="white" POINT-SIZE="10"><B>{table}</B></FONT>
                            </TD></TR>
                    '''
                    
                    # Agregar PKs
                    for col in table_info['columns']:
                        if col['name'] in table_info['primary_keys']:
                            label += f'''<TR>
                                <TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT"><B>🔑 {col['name']}</B></TD>
                                <TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT">PK</TD>
                            </TR>'''
                    
                    # Agregar FKs
                    fk_columns = []
                    for fk in table_info['foreign_keys']:
                        if fk['constrained_columns']:
                            fk_columns.extend(fk['constrained_columns'])
                            all_foreign_keys.append({
                                'from_table': table,
                                'to_table': fk['referred_table'],
                                'from_col': fk['constrained_columns'][0] if fk['constrained_columns'] else '',
                                'to_col': fk['referred_columns'][0] if fk['referred_columns'] else ''
                            })
                    
                    for col in table_info['columns']:
                        if col['name'] in fk_columns and col['name'] not in table_info['primary_keys']:
                            label += f'''<TR>
                                <TD BGCOLOR="{COLORS['fk_bg']}" ALIGN="LEFT">🔗 {col['name']}</TD>
                                <TD BGCOLOR="{COLORS['fk_bg']}" ALIGN="LEFT">FK</TD>
                            </TR>'''
                    
                    # Agregar algunos atributos importantes
                    count = 0
                    for col in table_info['columns']:
                        if (col['name'] not in table_info['primary_keys'] and 
                            col['name'] not in fk_columns and count < 3):
                            if any(kw in col['name'].lower() for kw in 
                                  ['nombre', 'fecha', 'monto', 'estado', 'activo']):
                                label += f'''<TR>
                                    <TD BGCOLOR="{COLORS['attribute_bg']}" ALIGN="LEFT" COLSPAN="2">
                                        {col['name']}
                                    </TD>
                                </TR>'''
                                count += 1
                    
                    label += '</TABLE>>'
                    subgraph.node(table, label=label)
                    print(f"  - {module_name}: {table}")
        
        # Agregar relaciones (foreign keys)
        for fk in all_foreign_keys:
            if fk['from_table'] in existing_tables and fk['to_table'] in existing_tables:
                label = f"{fk['from_col']}\n→\n{fk['to_col']}"
                dot.edge(
                    fk['from_table'],
                    fk['to_table'],
                    label=label,
                    arrowhead='crow',
                    arrowtail='none'
                )
        
        # Guardar diagrama
        output_path = self.output_dir / 'DER_Modular_Cantinatitadb'
        dot.render(output_path, cleanup=True)
        print(f"\n✓ DER Modular generado: {output_path}.png")
        return str(output_path) + '.png'
    
    def generate_module_diagrams(self):
        """Genera un diagrama individual para cada módulo"""
        print("\n" + "="*70)
        print("GENERANDO DIAGRAMAS INDIVIDUALES POR MÓDULO")
        print("="*70)
        
        existing_tables = set(self.inspector.get_table_names())
        generated_files = []
        
        for module_name, module_info in MODULES.items():
            tables_in_module = [t for t in module_info['tables'] if t in existing_tables]
            
            if not tables_in_module:
                continue
            
            dot = graphviz.Digraph(
                name=f'DER_{module_name.replace(" ", "_")}',
                comment=f'DER - Módulo {module_name}',
                format='png',
                engine='dot'
            )
            
            dot.attr(rankdir='LR', splines='ortho')
            dot.attr('node', shape='plaintext', fontname='Arial', fontsize='10')
            dot.attr('edge', color=COLORS['relation_color'], penwidth='2')
            
            dot.attr(label=f'MÓDULO: {module_name}\n'
                          f'Base de datos: {self.db_config["database"]}',
                    fontsize='14', fontname='Arial Bold', labelloc='t')
            
            # Agregar tablas del módulo
            for table in tables_in_module:
                table_info = self.get_table_info(table)
                if not table_info:
                    continue
                
                label = f'''<
                    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                        <TR><TD BGCOLOR="{module_info['border']}" COLSPAN="3">
                            <FONT COLOR="white" POINT-SIZE="11"><B>{table}</B></FONT>
                        </TD></TR>
                        <TR>
                            <TD BGCOLOR="#D3D3D3"><B>Column</B></TD>
                            <TD BGCOLOR="#D3D3D3"><B>Type</B></TD>
                            <TD BGCOLOR="#D3D3D3"><B>Key</B></TD>
                        </TR>
                '''
                
                for col in table_info['columns']:
                    col_name = col['name']
                    col_type = str(col['type'])[:20]
                    
                    key_type = ''
                    bgcolor = COLORS['attribute_bg']
                    
                    if col_name in table_info['primary_keys']:
                        key_type = 'PK'
                        bgcolor = COLORS['pk_bg']
                    
                    for fk in table_info['foreign_keys']:
                        if fk['constrained_columns'] and col_name in fk['constrained_columns']:
                            key_type = 'PK,FK' if key_type else 'FK'
                            bgcolor = COLORS['fk_bg']
                    
                    # Formatear key_type para evitar tags vacíos
                    key_display = f'<B>{key_type}</B>' if key_type else ''
                    
                    label += f'''<TR>
                        <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_name}</TD>
                        <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_type}</TD>
                        <TD BGCOLOR="{bgcolor}" ALIGN="CENTER">{key_display}</TD>
                    </TR>'''
                
                label += '</TABLE>>'
                dot.node(table, label=label)
            
            # Agregar relaciones dentro del módulo
            for table in tables_in_module:
                table_info = self.get_table_info(table)
                if not table_info:
                    continue
                
                for fk in table_info['foreign_keys']:
                    ref_table = fk['referred_table']
                    if ref_table in tables_in_module:
                        label = f"{fk['constrained_columns'][0]}" if fk['constrained_columns'] else ''
                        dot.edge(table, ref_table, label=label, arrowhead='crow')
            
            # Guardar
            safe_name = module_name.replace(' ', '_').replace('/', '_')
            output_path = self.output_dir / f'DER_Modulo_{safe_name}'
            dot.render(output_path, cleanup=True)
            generated_files.append(str(output_path) + '.png')
            print(f"  ✓ {module_name}: {output_path}.png")
        
        return generated_files
    
    def close(self):
        """Cierra la conexión"""
        if self.engine:
            self.engine.dispose()


def main():
    """Función principal"""
    print("="*70)
    print("GENERADOR DE DER MODULAR - CANTINATITADB")
    print("="*70)
    
    generator = ModularDERGenerator(DB_CONFIG)
    
    if not generator.connect():
        sys.exit(1)
    
    try:
        # Generar DER modular completo
        modular_path = generator.generate_modular_der()
        
        # Generar diagramas por módulo
        module_files = generator.generate_module_diagrams()
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO")
        print("="*70)
        print(f"\nDER Modular completo: {modular_path}")
        print(f"\nDiagramas por módulo ({len(module_files)}):")
        for f in module_files:
            print(f"  - {Path(f).name}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        generator.close()


if __name__ == '__main__':
    main()
