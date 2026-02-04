import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print('='*80)
print('ELIMINANDO TRIGGER PROBLEMÁTICO: trg_almuerzo_validar_plan_y_pago')
print('='*80)
print('\nEste trigger valida pagos anticipados que ya no usamos.')
print('Nuestro nuevo sistema usa CRÉDITO MENSUAL (se paga después).\n')

cursor = connection.cursor()

try:
    # Eliminar el trigger que valida pagos
    cursor.execute("DROP TRIGGER IF EXISTS trg_almuerzo_validar_plan_y_pago")
    print('✅ Trigger eliminado exitosamente\n')
    
    # Verificar triggers restantes
    cursor.execute("SHOW TRIGGERS WHERE `Table` = 'registro_consumo_almuerzo'")
    triggers_restantes = cursor.fetchall()
    
    print('TRIGGERS RESTANTES:')
    print('-'*80)
    for t in triggers_restantes:
        print(f'  • {t[0]} ({t[4]} {t[1]})')
    
    if not triggers_restantes:
        print('  (ninguno)')
    
    print('\n' + '='*80)
    print('✅ PROCESO COMPLETADO')
    print('='*80)
    print('\nAhora el sistema puede registrar almuerzos con crédito mensual.')
    print('Los pagos se realizarán al final del mes.\n')
    
except Exception as e:
    print(f'❌ ERROR: {e}')
finally:
    cursor.close()
