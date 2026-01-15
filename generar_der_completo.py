"""
Script para generar Diagrama Entidad-Relación (DER) completo de la base de datos 'cantinatitadb'
Genera dos diagramas:
1. DER Lógico: Muestra entidades y relaciones conceptuales
2. DER Físico: Muestra tablas, columnas, tipos de datos y constraints

Requisitos:
    - pip install sqlalchemy pymysql graphviz python-decouple
    - Tener instalado Graphviz en el sistema: https://graphviz.org/download/
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from decouple import config
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import graphviz

# Configuración de la base de datos desde settings
DB_CONFIG = {
    'host': config('DB_HOST', default='localhost'),
    'port': config('DB_PORT', default='3306'),
    'user': config('DB_USER', default='root'),
    'password': config('DB_PASSWORD'),
    'database': config('DB_NAME', default='cantinatitadb'),
}

# Colores para el diagrama
COLORS = {
    'entity_bg': '#E8F4F8',
    'entity_border': '#2E86AB',
    'pk_bg': '#FFE5B4',
    'fk_bg': '#C8E6C9',
    'attribute_bg': '#FFFFFF',
    'relation_color': '#FF6B35',
    'header_bg': '#1F4788',
}


class DERGenerator:
    """Generador de Diagramas Entidad-Relación"""
    
    def __init__(self, db_config):
        """Inicializa el generador con la configuración de la base de datos"""
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
            print(f"✓ Conexión exitosa a la base de datos '{self.db_config['database']}'")
            return True
        except SQLAlchemyError as e:
            print(f"✗ Error al conectar con la base de datos: {e}")
            return False
    
    def get_table_info(self, table_name):
        """Obtiene información detallada de una tabla"""
        try:
            columns = self.inspector.get_columns(table_name)
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            indexes = self.inspector.get_indexes(table_name)
            
            pk_columns = pk_constraint.get('constrained_columns', [])
            
            return {
                'columns': columns,
                'primary_keys': pk_columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        except Exception as e:
            print(f"Error obteniendo info de tabla {table_name}: {e}")
            return None
    
    def format_column_type(self, column_type):
        """Formatea el tipo de columna para visualización"""
        type_str = str(column_type)
        # Simplificar algunos tipos comunes
        type_str = type_str.replace('VARCHAR', 'VARCHAR')
        type_str = type_str.replace('INTEGER', 'INT')
        return type_str
    
    def generate_logical_der(self):
        """Genera el DER Lógico (conceptual)"""
        print("\n" + "="*70)
        print("GENERANDO DER LÓGICO")
        print("="*70)
        
        dot = graphviz.Digraph(
            name='DER_Logico_CantinatitaDB',
            comment='Diagrama Entidad-Relación Lógico - Base de Datos Cantina Tita',
            format='png',
            engine='dot'
        )
        
        # Configuración general del grafo
        dot.attr(rankdir='TB', splines='ortho', nodesep='1.0', ranksep='1.5')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor=COLORS['entity_bg'],
                fontname='Arial', fontsize='10', margin='0.2,0.1')
        dot.attr('edge', color=COLORS['relation_color'], fontname='Arial', 
                fontsize='9', penwidth='2')
        
        # Título
        dot.attr(label=f'DER LÓGICO - Base de Datos: {self.db_config["database"]}\n'
                      f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                fontsize='16', fontname='Arial Bold', labelloc='t')
        
        # Obtener todas las tablas
        tables = self.inspector.get_table_names()
        print(f"Total de tablas encontradas: {len(tables)}")
        
        # Crear nodos para cada tabla
        for table in sorted(tables):
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            # Crear etiqueta HTML para la entidad
            label = f'''<
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    <TR><TD BGCOLOR="{COLORS['header_bg']}" COLSPAN="2">
                        <FONT COLOR="white" POINT-SIZE="12"><B>{table.upper()}</B></FONT>
                    </TD></TR>
            '''
            
            # Agregar atributos clave (PK)
            for col in table_info['columns']:
                col_name = col['name']
                if col_name in table_info['primary_keys']:
                    label += f'''<TR><TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT">
                        <B>🔑 {col_name}</B></TD>
                        <TD BGCOLOR="{COLORS['pk_bg']}" ALIGN="LEFT"><I>PK</I></TD></TR>
                    '''
            
            # Agregar otros atributos importantes (no FK)
            fk_columns = [fk['constrained_columns'][0] for fk in table_info['foreign_keys'] 
                         if fk['constrained_columns']]
            
            for col in table_info['columns']:
                col_name = col['name']
                if col_name not in table_info['primary_keys'] and col_name not in fk_columns:
                    # Mostrar solo algunos atributos clave para no saturar
                    if any(keyword in col_name.lower() for keyword in 
                          ['nombre', 'fecha', 'monto', 'total', 'estado', 'tipo', 'activo']):
                        label += f'''<TR><TD BGCOLOR="{COLORS['attribute_bg']}" ALIGN="LEFT" COLSPAN="2">
                            {col_name}</TD></TR>
                        '''
            
            label += '</TABLE>>'
            
            dot.node(table, label=label, shape='plaintext')
        
        # Crear relaciones basadas en foreign keys
        relationships = {}
        for table in tables:
            table_info = self.get_table_info(table)
            if not table_info:
                continue
                
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                constrained_cols = fk['constrained_columns']
                referred_cols = fk['referred_columns']
                
                if constrained_cols and referred_cols:
                    key = f"{table}->{ref_table}"
                    if key not in relationships:
                        relationships[key] = {
                            'from': table,
                            'to': ref_table,
                            'columns': []
                        }
                    relationships[key]['columns'].append({
                        'from_col': constrained_cols[0],
                        'to_col': referred_cols[0]
                    })
        
        # Agregar las relaciones al diagrama
        for rel_key, rel_info in relationships.items():
            label = f"{len(rel_info['columns'])} FK"
            if len(rel_info['columns']) == 1:
                label = rel_info['columns'][0]['from_col']
            
            dot.edge(
                rel_info['from'],
                rel_info['to'],
                label=label,
                arrowhead='crow',
                arrowtail='none'
            )
        
        # Guardar diagrama
        output_path = self.output_dir / 'DER_Logico_Cantinatitadb'
        dot.render(output_path, cleanup=True)
        print(f"✓ DER Lógico generado: {output_path}.png")
        return str(output_path) + '.png'
    
    def generate_physical_der(self):
        """Genera el DER Físico (con detalles de columnas, tipos, constraints)"""
        print("\n" + "="*70)
        print("GENERANDO DER FÍSICO")
        print("="*70)
        
        dot = graphviz.Digraph(
            name='DER_Fisico_CantinatitaDB',
            comment='Diagrama Entidad-Relación Físico - Base de Datos Cantina Tita',
            format='png',
            engine='dot'
        )
        
        # Configuración general del grafo
        dot.attr(rankdir='TB', splines='polyline', nodesep='0.8', ranksep='1.2')
        dot.attr('node', shape='plaintext', fontname='Courier', fontsize='9')
        dot.attr('edge', color=COLORS['relation_color'], fontname='Arial', 
                fontsize='8', penwidth='1.5')
        
        # Título
        dot.attr(label=f'DER FÍSICO - Base de Datos: {self.db_config["database"]}\n'
                      f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                fontsize='14', fontname='Arial Bold', labelloc='t')
        
        # Obtener todas las tablas
        tables = self.inspector.get_table_names()
        print(f"Total de tablas encontradas: {len(tables)}")
        
        # Crear nodos detallados para cada tabla
        for table in sorted(tables):
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            # Crear etiqueta HTML para la tabla física
            label = f'''<
                <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3">
                    <TR><TD BGCOLOR="{COLORS['header_bg']}" COLSPAN="4">
                        <FONT COLOR="white" POINT-SIZE="11"><B>{table}</B></FONT>
                    </TD></TR>
                    <TR>
                        <TD BGCOLOR="#D3D3D3"><B>Column</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Type</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Null</B></TD>
                        <TD BGCOLOR="#D3D3D3"><B>Key</B></TD>
                    </TR>
            '''
            
            # Agregar todas las columnas con detalles
            for col in table_info['columns']:
                col_name = col['name']
                col_type = self.format_column_type(col['type'])
                nullable = 'YES' if col['nullable'] else 'NO'
                
                # Determinar el tipo de clave
                key_type = ''
                bgcolor = COLORS['attribute_bg']
                
                if col_name in table_info['primary_keys']:
                    key_type = 'PK'
                    bgcolor = COLORS['pk_bg']
                
                # Verificar si es FK
                for fk in table_info['foreign_keys']:
                    if fk['constrained_columns'] and col_name in fk['constrained_columns']:
                        if key_type:
                            key_type = 'PK,FK'
                        else:
                            key_type = 'FK'
                        bgcolor = COLORS['fk_bg']
                        break
                
                # Formatear key_type para evitar tags vacíos
                key_display = f'<B>{key_type}</B>' if key_type else ''
                
                label += f'''<TR>
                    <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_name}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="LEFT">{col_type}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="CENTER">{nullable}</TD>
                    <TD BGCOLOR="{bgcolor}" ALIGN="CENTER">{key_display}</TD>
                </TR>
                '''
            
            label += '</TABLE>>'
            
            dot.node(table, label=label)
            print(f"  - Tabla procesada: {table} ({len(table_info['columns'])} columnas)")
        
        # Crear relaciones detalladas basadas en foreign keys
        for table in tables:
            table_info = self.get_table_info(table)
            if not table_info:
                continue
                
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                constrained_cols = fk['constrained_columns']
                referred_cols = fk['referred_columns']
                
                if constrained_cols and referred_cols:
                    label = f"{constrained_cols[0]}\n→\n{referred_cols[0]}"
                    
                    dot.edge(
                        table,
                        ref_table,
                        label=label,
                        arrowhead='normal',
                        arrowtail='crow',
                        dir='both'
                    )
        
        # Guardar diagrama
        output_path = self.output_dir / 'DER_Fisico_Cantinatitadb'
        dot.render(output_path, cleanup=True)
        print(f"✓ DER Físico generado: {output_path}.png")
        return str(output_path) + '.png'
    
    def generate_statistics(self):
        """Genera estadísticas de la base de datos"""
        print("\n" + "="*70)
        print("ESTADÍSTICAS DE LA BASE DE DATOS")
        print("="*70)
        
        tables = self.inspector.get_table_names()
        total_tables = len(tables)
        total_columns = 0
        total_pks = 0
        total_fks = 0
        total_indexes = 0
        
        stats = []
        
        for table in tables:
            table_info = self.get_table_info(table)
            if not table_info:
                continue
            
            num_columns = len(table_info['columns'])
            num_pks = len(table_info['primary_keys'])
            num_fks = len(table_info['foreign_keys'])
            num_indexes = len(table_info['indexes'])
            
            total_columns += num_columns
            total_pks += num_pks
            total_fks += num_fks
            total_indexes += num_indexes
            
            stats.append({
                'table': table,
                'columns': num_columns,
                'pks': num_pks,
                'fks': num_fks,
                'indexes': num_indexes
            })
        
        print(f"\nTotal de tablas: {total_tables}")
        print(f"Total de columnas: {total_columns}")
        print(f"Total de Primary Keys: {total_pks}")
        print(f"Total de Foreign Keys: {total_fks}")
        print(f"Total de Índices: {total_indexes}")
        
        # Guardar estadísticas en archivo
        stats_file = self.output_dir / 'estadisticas_bd.txt'
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"ESTADÍSTICAS DE LA BASE DE DATOS: {self.db_config['database']}\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total de tablas: {total_tables}\n")
            f.write(f"Total de columnas: {total_columns}\n")
            f.write(f"Total de Primary Keys: {total_pks}\n")
            f.write(f"Total de Foreign Keys: {total_fks}\n")
            f.write(f"Total de Índices: {total_indexes}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("DETALLE POR TABLA\n")
            f.write("-"*70 + "\n")
            f.write(f"{'Tabla':<40} {'Cols':<6} {'PKs':<5} {'FKs':<5} {'Idx':<5}\n")
            f.write("-"*70 + "\n")
            
            for stat in sorted(stats, key=lambda x: x['table']):
                f.write(f"{stat['table']:<40} {stat['columns']:<6} {stat['pks']:<5} "
                       f"{stat['fks']:<5} {stat['indexes']:<5}\n")
        
        print(f"\n✓ Estadísticas guardadas en: {stats_file}")
        return str(stats_file)
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.engine:
            self.engine.dispose()
            print("\n✓ Conexión cerrada")


def main():
    """Función principal"""
    print("="*70)
    print("GENERADOR DE DER - BASE DE DATOS CANTINATITADB")
    print("="*70)
    print(f"Base de datos: {DB_CONFIG['database']}")
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Usuario: {DB_CONFIG['user']}")
    print("="*70)
    
    # Crear generador
    generator = DERGenerator(DB_CONFIG)
    
    # Conectar a la base de datos
    if not generator.connect():
        print("\n✗ No se pudo conectar a la base de datos")
        print("Verifica las credenciales en el archivo .env")
        sys.exit(1)
    
    try:
        # Generar estadísticas
        generator.generate_statistics()
        
        # Generar DER Lógico
        logical_path = generator.generate_logical_der()
        
        # Generar DER Físico
        physical_path = generator.generate_physical_der()
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"\nArchivos generados en: {generator.output_dir.absolute()}")
        print(f"  - DER Lógico: {logical_path}")
        print(f"  - DER Físico: {physical_path}")
        print(f"  - Estadísticas: {generator.output_dir / 'estadisticas_bd.txt'}")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n✗ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        generator.close()


if __name__ == '__main__':
    main()
