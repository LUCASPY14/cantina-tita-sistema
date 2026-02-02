"""
Script para corregir referencias en gestion/models.py
Ejecutar: python fix_models.py
"""

def fix_models():
    with open('gestion/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de correcciones a aplicar
    corrections = {
        # Corregir referencias a CompraProveedor -> Compras
        "# id_compra = models.ForeignKey(  # COMENTADO: Modelo CompraProveedor no existe": 
        "id_compra = models.ForeignKey(",
        
        "#     Compras,": 
        "        Compras,",
        
        "#     on_delete=models.CASCADE,": 
        "        on_delete=models.CASCADE,",
        
        "#     on_delete=models.SET_NULL,": 
        "        on_delete=models.SET_NULL,",
        
        "#     db_column='ID_Compra',": 
        "        db_column='ID_Compra',",
        
        "#     related_name='detalles'": 
        "        related_name='detalles'",
        
        "#     blank=True,": 
        "        blank=True,",
        
        "#     null=True": 
        "        null=True",
        
        "# )": 
        "    )",
        
        # Corregir referencias a Venta -> Ventas
        "# id_venta = models.ForeignKey(  # COMENTADO: Modelo Venta no existe en gestion":
        "id_venta = models.ForeignKey(",
        
        "#     Ventas,":
        "        Ventas,",
        
        "#     related_name='detalles'":
        "        related_name='detalles'",
        
        "#     related_name='pagos'":
        "        related_name='pagos'",
        
        "#     related_name='promociones_aplicadas'":
        "        related_name='promociones_aplicadas'",
        
        "# #     venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')  # COMENTADO: Modelo Venta no existe en gestion":
        "",  # Eliminar estas líneas comentadas
        
        "# #     cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas', null=True, blank=True)  # COMENTADO: Modelo Venta no existe en gestion":
        "",
        
        "# #     usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventas_realizadas')  # COMENTADO: Modelo Venta no existe en gestion":
        "",
        
        "# #     proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')  # COMENTADO: Modelo CompraProveedor no existe":
        "",
        
        "# #     usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='compras_realizadas')  # COMENTADO: Modelo CompraProveedor no existe":
        "",
        
        "# #     compra = models.ForeignKey(CompraProveedor, on_delete=models.CASCADE, related_name='detalles')  # COMENTADO: Modelo CompraProveedor no existe":
        "",
        
        # Corregir import de terminos_legales_model si existe
        "import gestion\nfrom gestion.terminos_legales_model import AceptacionTerminosSaldoNegativo":
        "# import gestion\n# from gestion.terminos_legales_model import AceptacionTerminosSaldoNegativo  # Descomentar si existe el archivo",
    }
    
    # Aplicar correcciones
    for old, new in corrections.items():
        content = content.replace(old, new)
    
    # Guardar archivo corregido
    with open('gestion/models_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo models_fixed.py creado exitosamente")
    print("\nPróximos pasos:")
    print("1. Revisa gestion/models_fixed.py")
    print("2. Si está correcto, renombra:")
    print("   - mv gestion/models.py gestion/models_old.py")
    print("   - mv gestion/models_fixed.py gestion/models.py")
    print("3. Ejecuta las migraciones limpias")

if __name__ == '__main__':
    fix_models()
