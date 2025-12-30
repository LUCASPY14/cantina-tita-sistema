from pathlib import Path
p=Path('gestion/cliente_views.py')
s=p.read_text(encoding='utf-8')
new=s.replace("pos:portal_login","clientes:portal_login")
count=s.count("pos:portal_login")
if count==0:
    print('No occurrences found')
else:
    p.write_text(new,encoding='utf-8')
    print(f'Replaced {count} occurrences of pos:portal_login -> clientes:portal_login')
