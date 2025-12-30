"""
Script para generar reporte de usuarios web (UsuariosWebClientes)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import UsuariosWebClientes

def generar_reporte_usuario_web():
    print("=" * 60)
    print("REPORTE DE USUARIOS WEB (UsuariosWebClientes)")
    print("=" * 60)

    # Total de usuarios web
    total_usuarios = UsuariosWebClientes.objects.count()
    print(f"\nTotal de usuarios web: {total_usuarios}")

    # Usuarios activos
    usuarios_activos = UsuariosWebClientes.objects.filter(activo=True).count()
    print(f"Usuarios activos: {usuarios_activos}")

    # Usuarios inactivos
    usuarios_inactivos = UsuariosWebClientes.objects.filter(activo=False).count()
    print(f"Usuarios inactivos: {usuarios_inactivos}")

    # Usuarios con último acceso
    usuarios_con_acceso = UsuariosWebClientes.objects.filter(ultimo_acceso__isnull=False).count()
    print(f"Usuarios con último acceso registrado: {usuarios_con_acceso}")

    # Usuarios sin último acceso
    usuarios_sin_acceso = UsuariosWebClientes.objects.filter(ultimo_acceso__isnull=True).count()
    print(f"Usuarios sin último acceso registrado: {usuarios_sin_acceso}")

    if total_usuarios > 0:
        print(".1f")
        print(".1f")

    print("\n" + "=" * 60)
    print("DETALLE DE USUARIOS:")
    print("=" * 60)

    # Listar usuarios (limitado a 20 para no sobrecargar)
    usuarios = UsuariosWebClientes.objects.select_related('id_cliente').order_by('usuario')[:20]
    for usuario in usuarios:
        estado = "ACTIVO" if usuario.activo else "INACTIVO"
        ultimo_acceso = usuario.ultimo_acceso.strftime('%Y-%m-%d %H:%M') if usuario.ultimo_acceso else "Nunca"
        print(f"Usuario: {usuario.usuario}")
        print(f"  Cliente: {usuario.id_cliente.nombre_completo}")
        print(f"  Estado: {estado}")
        print(f"  Último acceso: {ultimo_acceso}")
        print("-" * 40)

    if total_usuarios > 20:
        print(f"\n... y {total_usuarios - 20} usuarios más")

if __name__ == "__main__":
    generar_reporte_usuario_web()