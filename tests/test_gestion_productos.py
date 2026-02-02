"""
Tests para Gestión de Productos
================================
Pruebas del módulo completo de gestión de productos y categorías
"""

import os
import sys
import django
from decimal import Decimal
from io import StringIO
import csv

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gestion.models import (
    Producto, Categoria, UnidadMedida, Impuesto, StockUnico,
    Alergeno, ProductoAlergeno
)
from gestion.forms_productos import ProductoForm, CategoriaForm


class ProductoCRUDTestCase(TestCase):
    """Tests para CRUD de Productos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos de prueba
        self.categoria = Categoria.objects.create(
            nombre='Bebidas Test',
            activo=True
        )
        
        self.unidad = UnidadMedida.objects.create(
            nombre='Unidad Test',
            abreviatura='UN',
            activo=True
        )
        
        self.impuesto = Impuesto.objects.create(
            descripcion='IVA 10% Test',
            porcentaje=Decimal('10.00'),
            activo=True
        )
        
        self.alergeno = Alergeno.objects.create(
            nombre='Maní Test',
            palabras_clave=['mani', 'peanut'],
            nivel_severidad='CRITICO',
            activo=True
        )
    
    def test_01_crear_producto_form_valido(self):
        """Test: Crear producto con formulario válido"""
        print("\n🧪 Test 1: Crear producto con formulario válido")
        
        form_data = {
            'codigo_barra': 'TEST001',
            'descripcion': 'Coca Cola Test 500ml',
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'stock_minimo': Decimal('10.000'),
            'permite_stock_negativo': False,
            'activo': True,
            'alergenos': [self.alergeno.id_alergeno]
        }
        
        form = ProductoForm(data=form_data)
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        producto = form.save()
        
        # Verificar que se creó correctamente
        self.assertEqual(producto.codigo_barra, 'TEST001')
        self.assertEqual(producto.descripcion, 'Coca Cola Test 500ml')
        self.assertEqual(producto.id_categoria, self.categoria)
        
        # Verificar que se asoció el alérgeno
        alergenos_asociados = ProductoAlergeno.objects.filter(id_producto=producto)
        self.assertEqual(alergenos_asociados.count(), 1)
        
        print(f"✅ Producto creado: {producto}")
        print(f"   Alérgenos: {alergenos_asociados.count()}")
    
    def test_02_crear_producto_codigo_duplicado(self):
        """Test: Validar que no se permitan códigos de barras duplicados"""
        print("\n🧪 Test 2: Código de barras duplicado")
        
        # Crear primer producto
        Producto.objects.create(
            codigo_barra='DUP001',
            descripcion='Producto Original',
            id_categoria=self.categoria,
            id_unidad_de_medida=self.unidad,
            id_impuesto=self.impuesto,
            activo=True
        )
        
        # Intentar crear segundo producto con mismo código
        form_data = {
            'codigo_barra': 'DUP001',  # Duplicado
            'descripcion': 'Producto Duplicado',
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'activo': True
        }
        
        form = ProductoForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_barra', form.errors)
        
        print(f"✅ Error de duplicado detectado correctamente")
        print(f"   Mensaje: {form.errors['codigo_barra'][0]}")
    
    def test_03_crear_producto_via_vista(self):
        """Test: Crear producto mediante vista HTTP"""
        print("\n🧪 Test 3: Crear producto vía POST request")
        
        url = reverse('crear_producto')
        
        response = self.client.post(url, {
            'codigo_barra': 'HTTP001',
            'descripcion': 'Producto vía HTTP',
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'stock_minimo': 15,
            'activo': True
        })
        
        # Debe redirigir después de crear
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el producto
        producto = Producto.objects.get(codigo_barra='HTTP001')
        self.assertEqual(producto.descripcion, 'Producto vía HTTP')
        
        # Verificar que se creó el stock inicial
        stock = StockUnico.objects.get(id_producto=producto)
        self.assertEqual(stock.stock_actual, Decimal('0.000'))
        
        print(f"✅ Producto creado vía HTTP")
        print(f"   ID: {producto.id_producto}")
        print(f"   Stock inicial: {stock.stock_actual}")
    
    def test_04_editar_producto(self):
        """Test: Editar producto existente"""
        print("\n🧪 Test 4: Editar producto existente")
        
        # Crear producto inicial
        producto = Producto.objects.create(
            codigo_barra='EDIT001',
            descripcion='Producto Original',
            id_categoria=self.categoria,
            id_unidad_de_medida=self.unidad,
            id_impuesto=self.impuesto,
            stock_minimo=Decimal('5.000'),
            activo=True
        )
        
        # Editar mediante formulario
        form_data = {
            'codigo_barra': 'EDIT001',
            'descripcion': 'Producto Modificado',  # Cambio
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'stock_minimo': Decimal('20.000'),  # Cambio
            'permite_stock_negativo': True,  # Cambio
            'activo': True
        }
        
        form = ProductoForm(data=form_data, instance=producto)
        self.assertTrue(form.is_valid())
        
        producto_editado = form.save()
        
        # Verificar cambios
        self.assertEqual(producto_editado.descripcion, 'Producto Modificado')
        self.assertEqual(producto_editado.stock_minimo, Decimal('20.000'))
        self.assertTrue(producto_editado.permite_stock_negativo)
        
        print(f"✅ Producto editado correctamente")
        print(f"   Descripción: {producto_editado.descripcion}")
        print(f"   Stock mínimo: {producto_editado.stock_minimo}")


class CategoriaCRUDTestCase(TestCase):
    """Tests para CRUD de Categorías"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_05_crear_categoria_simple(self):
        """Test: Crear categoría sin padre"""
        print("\n🧪 Test 5: Crear categoría simple")
        
        form_data = {
            'nombre': 'Bebidas',
            'activo': True
        }
        
        form = CategoriaForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        categoria = form.save()
        
        self.assertEqual(categoria.nombre, 'Bebidas')
        self.assertIsNone(categoria.id_categoria_padre)
        self.assertTrue(categoria.activo)
        
        print(f"✅ Categoría creada: {categoria.nombre}")
    
    def test_06_crear_subcategoria(self):
        """Test: Crear categoría con padre (subcategoría)"""
        print("\n🧪 Test 6: Crear subcategoría")
        
        # Crear categoría padre
        padre = Categoria.objects.create(
            nombre='Bebidas',
            activo=True
        )
        
        # Crear subcategoría
        form_data = {
            'nombre': 'Gaseosas',
            'id_categoria_padre': padre.id_categoria,
            'activo': True
        }
        
        form = CategoriaForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        subcategoria = form.save()
        
        self.assertEqual(subcategoria.nombre, 'Gaseosas')
        self.assertEqual(subcategoria.id_categoria_padre, padre)
        
        print(f"✅ Subcategoría creada")
        print(f"   Padre: {padre.nombre}")
        print(f"   Hijo: {subcategoria.nombre}")
    
    def test_07_validar_nombre_categoria_duplicado(self):
        """Test: No permitir nombres de categoría duplicados"""
        print("\n🧪 Test 7: Nombre de categoría duplicado")
        
        # Crear primera categoría
        Categoria.objects.create(nombre='Snacks', activo=True)
        
        # Intentar crear segunda con mismo nombre
        form_data = {
            'nombre': 'Snacks',  # Duplicado
            'activo': True
        }
        
        form = CategoriaForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        
        print(f"✅ Duplicado detectado correctamente")
    
    def test_08_eliminar_categoria_sin_productos(self):
        """Test: Eliminar categoría vacía"""
        print("\n🧪 Test 8: Eliminar categoría sin productos")
        
        categoria = Categoria.objects.create(
            nombre='Categoría Vacía',
            activo=True
        )
        
        categoria_id = categoria.id_categoria
        categoria.delete()
        
        # Verificar que se eliminó
        existe = Categoria.objects.filter(id_categoria=categoria_id).exists()
        self.assertFalse(existe)
        
        print(f"✅ Categoría eliminada correctamente")


class AlergenosTestCase(TestCase):
    """Tests para asociación de alérgenos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.categoria = Categoria.objects.create(nombre='Test', activo=True)
        self.unidad = UnidadMedida.objects.create(nombre='Test', abreviatura='T', activo=True)
        self.impuesto = Impuesto.objects.create(descripcion='Test', porcentaje=10, activo=True)
        
        self.alergeno1 = Alergeno.objects.create(
            nombre='Gluten',
            palabras_clave=['gluten', 'trigo'],
            nivel_severidad='ALTO',
            activo=True
        )
        
        self.alergeno2 = Alergeno.objects.create(
            nombre='Lactosa',
            palabras_clave=['lactosa', 'leche'],
            nivel_severidad='MEDIO',
            activo=True
        )
    
    def test_09_asociar_multiples_alergenos(self):
        """Test: Asociar múltiples alérgenos a un producto"""
        print("\n🧪 Test 9: Asociar múltiples alérgenos")
        
        form_data = {
            'codigo_barra': 'ALERG001',
            'descripcion': 'Pan con Leche',
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'activo': True,
            'alergenos': [self.alergeno1.id_alergeno, self.alergeno2.id_alergeno]
        }
        
        form = ProductoForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        producto = form.save()
        
        # Verificar asociaciones
        alergenos_asociados = ProductoAlergeno.objects.filter(id_producto=producto)
        self.assertEqual(alergenos_asociados.count(), 2)
        
        nombres_alergenos = [
            pa.id_alergeno.nombre for pa in alergenos_asociados
        ]
        self.assertIn('Gluten', nombres_alergenos)
        self.assertIn('Lactosa', nombres_alergenos)
        
        print(f"✅ Alérgenos asociados: {nombres_alergenos}")
    
    def test_10_editar_alergenos_producto(self):
        """Test: Modificar alérgenos de producto existente"""
        print("\n🧪 Test 10: Editar alérgenos de producto")
        
        # Crear producto con 1 alérgeno
        producto = Producto.objects.create(
            codigo_barra='ALERG002',
            descripcion='Producto Test',
            id_categoria=self.categoria,
            id_unidad_de_medida=self.unidad,
            id_impuesto=self.impuesto,
            activo=True
        )
        
        ProductoAlergeno.objects.create(
            id_producto=producto,
            id_alergeno=self.alergeno1
        )
        
        # Editar para cambiar a otro alérgeno
        form_data = {
            'codigo_barra': 'ALERG002',
            'descripcion': 'Producto Test',
            'id_categoria': self.categoria.id_categoria,
            'id_unidad_de_medida': self.unidad.id_unidad_de_medida,
            'id_impuesto': self.impuesto.id_impuesto,
            'activo': True,
            'alergenos': [self.alergeno2.id_alergeno]  # Cambio
        }
        
        form = ProductoForm(data=form_data, instance=producto)
        self.assertTrue(form.is_valid())
        
        form.save()
        
        # Verificar que se actualizaron los alérgenos
        alergenos_actuales = ProductoAlergeno.objects.filter(id_producto=producto)
        self.assertEqual(alergenos_actuales.count(), 1)
        self.assertEqual(
            alergenos_actuales.first().id_alergeno.nombre,
            'Lactosa'
        )
        
        print(f"✅ Alérgenos actualizados correctamente")


def ejecutar_tests():
    """Ejecutar todos los tests"""
    import unittest
    
    print("\n" + "="*60)
    print("TESTS: GESTION DE PRODUCTOS Y CATEGORIAS")
    print("="*60)
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(ProductoCRUDTestCase))
    suite.addTests(loader.loadTestsFromTestCase(CategoriaCRUDTestCase))
    suite.addTests(loader.loadTestsFromTestCase(AlergenosTestCase))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("TODOS LOS TESTS PASARON")
    else:
        print(f"{len(result.failures + result.errors)} TEST(S) FALLARON")
    print("="*60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Ejecutar tests
    resultado = ejecutar_tests()
    
    # Salir con código apropiado
    sys.exit(0 if resultado == 0 else 1)
