import re

# Leer archivo
with open('gestion/cliente_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar redirect('portal_login') por redirect('clientes:portal_login')
content = re.sub(r"redirect\('portal_login'\)", "redirect('clientes:portal_login')", content)

# Guardar archivo
with open('gestion/cliente_views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Reemplazos completados exitosamente')
