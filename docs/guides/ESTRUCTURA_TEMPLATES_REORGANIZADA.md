# REORGANIZACIÓN PROFESIONAL DE TEMPLATES

## ESTRUCTURA ACTUAL: 173 templates con duplicaciones

### PROBLEMAS IDENTIFICADOS:
- 10 archivos "dashboard.html" duplicados
- 4 archivos "lista.html" duplicados  
- 3 archivos "crear.html" duplicados
- Carpetas mixtas (apps/gestion tiene subcarpetas y archivos sueltos)
- Inconsistencia en nomenclatura
- Templates base dispersos

## NUEVA ESTRUCTURA PROFESIONAL:

```
frontend/templates/
├── base/                          # Templates base del sistema
│   ├── base.html                  # Template base principal
│   ├── base_admin.html           # Base para área administrativa
│   ├── base_portal.html          # Base para portal de padres
│   ├── base_pos.html             # Base para punto de venta
│   └── base_auth.html            # Base para autenticación
│
├── components/                    # Componentes reutilizables
│   ├── forms/                    # Formularios comunes
│   ├── modals/                   # Modales reutilizables
│   ├── navigation/               # Elementos de navegación
│   └── widgets/                  # Widgets específicos
│
├── auth/                         # Sistema de autenticación
│   ├── login.html
│   ├── register.html
│   ├── password_reset.html
│   └── two_factor/
│
├── admin/                        # Área administrativa
│   ├── dashboard/
│   ├── users/
│   └── settings/
│
├── portal/                       # Portal de padres/clientes
│   ├── dashboard/
│   ├── payments/
│   ├── children/
│   └── profile/
│
├── pos/                          # Punto de venta
│   ├── dashboard/
│   ├── sales/
│   ├── inventory/
│   ├── reports/
│   └── cash_register/
│
├── gestion/                      # Gestión interna
│   ├── dashboard/
│   ├── products/
│   ├── categories/
│   ├── clients/
│   ├── employees/
│   └── reports/
│
├── emails/                       # Templates de emails
│   ├── notifications/
│   ├── reminders/
│   └── confirmations/
│
└── errors/                       # Páginas de error
    ├── 404.html
    ├── 500.html
    └── maintenance.html
```

## CONVENCIONES DE NOMENCLATURA:
- dashboard.html → dashboard_main.html (principal)
- dashboard_[modulo].html (específicos)
- [entidad]_list.html para listados
- [entidad]_form.html para formularios
- [entidad]_detail.html para detalles
- [accion]_[entidad].html para acciones específicas

## PLAN DE REORGANIZACIÓN:
1. Crear nueva estructura de directorios
2. Mover templates base a /base/
3. Consolidar componentes en /components/
4. Reorganizar por módulos funcionales
5. Renombrar archivos duplicados con sufijos específicos
6. Actualizar referencias en views.py
7. Validar funcionamiento completo