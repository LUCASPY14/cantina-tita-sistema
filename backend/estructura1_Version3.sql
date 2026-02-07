-- Base cantinatitadb (núcleo Django + dominio operativo), con:
-- - CHECK corregidos (nombres exactos)
-- - Saldo negativo condicionado en tarjetas
-- - Dinero en BIGINT, cantidades DECIMAL solo donde aplica
-- - PK id_* AUTO_INCREMENT en operativas; claves naturales únicas aparte
-- - NOT NULL + defaults en campos críticos
-- - Sin índices duplicados
-- - Modelo relacional para restricciones/alergenos (tablas puente con notas)

CREATE DATABASE IF NOT EXISTS cantinatitadb
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE cantinatitadb;

-- =========================================================
-- Núcleo Django (auth / contenttypes / admin / sessions)
-- =========================================================
CREATE TABLE django_migrations (
  id INT NOT NULL AUTO_INCREMENT,
  app VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  applied DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_django_migrations_app_name (app, name)
);

CREATE TABLE django_content_type (
  id INT NOT NULL AUTO_INCREMENT,
  app_label VARCHAR(100) NOT NULL,
  model VARCHAR(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_django_content_type_app_model (app_label, model)
);

CREATE TABLE auth_permission (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  content_type_id INT NOT NULL,
  codename VARCHAR(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_permission_ct_codename (content_type_id, codename),
  KEY idx_auth_permission_content_type (content_type_id),
  CONSTRAINT fk_auth_permission_content_type FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE auth_group (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_group_name (name)
);

CREATE TABLE auth_group_permissions (
  id INT NOT NULL AUTO_INCREMENT,
  group_id INT NOT NULL,
  permission_id INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_group_permissions (group_id, permission_id),
  KEY idx_auth_group_permissions_permission (permission_id),
  CONSTRAINT fk_auth_group_permissions_group FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_auth_group_permissions_permission FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE auth_user (
  id INT NOT NULL AUTO_INCREMENT,
  password VARCHAR(128) NOT NULL DEFAULT '',
  last_login DATETIME(6) DEFAULT NULL,
  is_superuser TINYINT(1) NOT NULL DEFAULT 0,
  username VARCHAR(150) NOT NULL,
  first_name VARCHAR(150) NOT NULL DEFAULT '',
  last_name VARCHAR(150) NOT NULL DEFAULT '',
  email VARCHAR(254) NOT NULL DEFAULT '',
  is_staff TINYINT(1) NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  date_joined DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_user_username (username),
  KEY idx_auth_user_email (email),
  KEY idx_auth_user_is_active (is_active)
);

CREATE TABLE auth_user_groups (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  group_id INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_user_groups (user_id, group_id),
  KEY idx_auth_user_groups_group (group_id),
  CONSTRAINT fk_auth_user_groups_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_auth_user_groups_group FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE auth_user_user_permissions (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  permission_id INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_user_permissions (user_id, permission_id),
  KEY idx_auth_user_permissions_permission (permission_id),
  CONSTRAINT fk_auth_user_permissions_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_auth_user_permissions_permission FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE django_admin_log (
  id INT NOT NULL AUTO_INCREMENT,
  action_time DATETIME(6) NOT NULL,
  object_id LONGTEXT,
  object_repr VARCHAR(200) NOT NULL,
  action_flag SMALLINT UNSIGNED NOT NULL,
  change_message LONGTEXT NOT NULL,
  content_type_id INT DEFAULT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_django_admin_log_content_type (content_type_id),
  KEY idx_django_admin_log_user (user_id),
  CONSTRAINT chk_django_admin_log_action_flag CHECK (action_flag >= 0),
  CONSTRAINT fk_django_admin_log_content_type FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_django_admin_log_user FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE django_session (
  session_key VARCHAR(40) NOT NULL,
  session_data LONGTEXT NOT NULL,
  expire_date DATETIME(6) NOT NULL,
  PRIMARY KEY (session_key),
  KEY idx_django_session_expire_date (expire_date)
);

-- =========================================================
-- Catálogos base
-- =========================================================
CREATE TABLE unidades_medida (
  id_unidad_de_medida INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL,
  abreviatura VARCHAR(10) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_unidad_de_medida),
  UNIQUE KEY uk_unidad_nombre (nombre)
);

CREATE TABLE categorias (
  id_categoria INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  id_categoria_padre INT DEFAULT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_categoria),
  UNIQUE KEY uk_categorias_nombre (nombre),
  KEY fk_categoria_padre (id_categoria_padre),
  CONSTRAINT fk_categoria_padre FOREIGN KEY (id_categoria_padre) REFERENCES categorias(id_categoria) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE tipos_cliente (
  id_tipo_cliente INT NOT NULL AUTO_INCREMENT,
  nombre_tipo VARCHAR(50) NOT NULL,
  descripcion VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_tipo_cliente),
  UNIQUE KEY uk_tipos_cliente_nombre (nombre_tipo)
);

CREATE TABLE tipos_rol_general (
  id_rol INT NOT NULL AUTO_INCREMENT,
  nombre_rol VARCHAR(50) NOT NULL,
  descripcion VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_rol),
  UNIQUE KEY uk_roles_nombre (nombre_rol)
);

CREATE TABLE medios_pago (
  id_medio_pago INT NOT NULL AUTO_INCREMENT,
  descripcion VARCHAR(50) NOT NULL,
  genera_comision TINYINT(1) NOT NULL DEFAULT 0,
  requiere_validacion TINYINT(1) NOT NULL DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_medio_pago),
  UNIQUE KEY uk_medios_pago_desc (descripcion)
);

CREATE TABLE tipos_pago (
  id_tipo_pago INT NOT NULL AUTO_INCREMENT,
  descripcion VARCHAR(50) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_tipo_pago),
  UNIQUE KEY uk_tipos_pago_desc (descripcion)
);

CREATE TABLE alergenos (
  id_alergeno INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  palabras_clave JSON,
  nivel_severidad ENUM('CRITICO','ALTO','MEDIO','BAJO') DEFAULT 'MEDIO',
  icono VARCHAR(10),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  usuario_creacion VARCHAR(100),
  PRIMARY KEY (id_alergeno),
  UNIQUE KEY uk_alergenos_nombre (nombre),
  KEY idx_alergenos_activo (activo),
  KEY idx_alergenos_severidad (nivel_severidad)
);

CREATE TABLE restricciones (
  id_restriccion INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  tipo ENUM('DIETARIA','OPERATIVA','OTRA') NOT NULL DEFAULT 'DIETARIA',
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_restriccion),
  UNIQUE KEY uk_restricciones_nombre (nombre)
);

CREATE TABLE impuestos (
  id_impuesto INT NOT NULL AUTO_INCREMENT,
  nombre_impuesto VARCHAR(50) NOT NULL,
  porcentaje DECIMAL(4,2) NOT NULL,
  vigente_desde DATE,
  vigente_hasta DATE,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_impuesto),
  UNIQUE KEY uk_impuestos_nombre (nombre_impuesto),
  CONSTRAINT chk_impuestos_rango CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde)
);

-- CORRECCIÓN: Tabla unidades_empresa sin CHECK en columna AUTO_INCREMENT
CREATE TABLE unidades_empresa (
  id_empresa INT NOT NULL AUTO_INCREMENT,
  ruc VARCHAR(20),
  razon_social VARCHAR(255),
  direccion VARCHAR(255),
  ciudad VARCHAR(100),
  pais VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_empresa)
);

-- =========================================================
-- Listas de precios / Productos / Promociones
-- =========================================================
CREATE TABLE listas_precios (
  id_lista INT NOT NULL AUTO_INCREMENT,
  nombre_lista VARCHAR(100) NOT NULL,
  fecha_vigencia DATE,
  moneda VARCHAR(3),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_lista),
  UNIQUE KEY uk_listas_nombre (nombre_lista)
);

-- =========================================================
-- Clientes / Empleados / Hijos
-- =========================================================
CREATE TABLE clientes (
  id_cliente INT NOT NULL AUTO_INCREMENT,
  id_lista INT DEFAULT NULL,
  id_tipo_cliente INT DEFAULT NULL,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  razon_social VARCHAR(255),
  ruc_ci VARCHAR(20) NOT NULL,
  direccion VARCHAR(255),
  ciudad VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(100),
  limite_credito BIGINT NOT NULL DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_cliente),
  UNIQUE KEY uk_clientes_ruc_ci (ruc_ci),
  KEY fk_clientes_lista (id_lista),
  KEY fk_clientes_tipo (id_tipo_cliente),
  KEY idx_cliente_nombre (nombres, apellidos),
  KEY idx_cliente_apellidos (apellidos, nombres),
  KEY idx_cliente_telefono (telefono),
  KEY idx_clientes_activo_credito (activo, limite_credito),
  CONSTRAINT fk_clientes_tipo FOREIGN KEY (id_tipo_cliente) REFERENCES tipos_cliente(id_tipo_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_clientes_lista FOREIGN KEY (id_lista) REFERENCES listas_precios(id_lista) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_clientes_limite CHECK (limite_credito >= 0)
);

CREATE TABLE empleados (
  id_empleado INT NOT NULL AUTO_INCREMENT,
  id_rol INT DEFAULT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  usuario VARCHAR(50) NOT NULL,
  contrasena_hash CHAR(60),
  fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
  direccion VARCHAR(255),
  ciudad VARCHAR(100),
  pais VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_baja DATETIME DEFAULT NULL,
  PRIMARY KEY (id_empleado),
  UNIQUE KEY uk_empleado_usuario (usuario),
  KEY fk_empleado_rol (id_rol),
  KEY idx_empleado_activo (activo, id_rol),
  KEY idx_empleado_nombre (nombre, apellido),
  CONSTRAINT fk_empleado_rol FOREIGN KEY (id_rol) REFERENCES tipos_rol_general(id_rol) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE hijos (
  id_hijo INT NOT NULL AUTO_INCREMENT,
  id_cliente_responsable INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  fecha_nacimiento DATE,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  foto_perfil VARCHAR(255),
  fecha_foto DATETIME,
  grado VARCHAR(50),
  PRIMARY KEY (id_hijo),
  KEY fk_hijo_cliente (id_cliente_responsable),
  KEY idx_hijo_grado (grado, activo),
  CONSTRAINT fk_hijo_cliente FOREIGN KEY (id_cliente_responsable) REFERENCES clientes(id_cliente) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE historial_grados_hijos (
  id_historial INT NOT NULL AUTO_INCREMENT,
  id_hijo INT NOT NULL,
  grado_anterior VARCHAR(50),
  grado_nuevo VARCHAR(50),
  anio_escolar INT,
  fecha_cambio TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  motivo ENUM('INGRESO','PROMOCION','CAMBIO_MANUAL','REINGRESO'),
  usuario_registro VARCHAR(100),
  observaciones TEXT,
  PRIMARY KEY (id_historial),
  KEY idx_historial_hijo (id_hijo),
  KEY idx_historial_anio (anio_escolar),
  CONSTRAINT fk_historial_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE CASCADE
);

CREATE TABLE productos (
  id_producto INT NOT NULL AUTO_INCREMENT,
  id_categoria INT DEFAULT NULL,
  id_unidad_de_medida INT DEFAULT NULL,
  id_impuesto INT DEFAULT NULL,
  codigo_barra VARCHAR(50),
  descripcion VARCHAR(255) NOT NULL,
  stock_minimo DECIMAL(10,3) NOT NULL DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  permite_stock_negativo TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id_producto),
  UNIQUE KEY uk_producto_codigo (codigo_barra),
  KEY fk_producto_categoria (id_categoria),
  KEY fk_producto_unidad (id_unidad_de_medida),
  KEY fk_producto_impuesto (id_impuesto),
  KEY idx_producto_descripcion (descripcion(50)),
  FULLTEXT KEY idx_producto_descripcion_fulltext (descripcion),
  CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_producto_unidad FOREIGN KEY (id_unidad_de_medida) REFERENCES unidades_medida(id_unidad_de_medida) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_producto_impuesto FOREIGN KEY (id_impuesto) REFERENCES impuestos(id_impuesto) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_producto_stock_minimo CHECK (stock_minimo >= 0)
);

CREATE TABLE precios_por_lista (
  id_precio INT NOT NULL AUTO_INCREMENT,
  id_producto INT NOT NULL,
  id_lista INT NOT NULL,
  precio_unitario_neto BIGINT NOT NULL,
  fecha_vigencia DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_precio),
  UNIQUE KEY uk_precio_producto_lista (id_producto, id_lista),
  KEY fk_ppl_lista (id_lista),
  CONSTRAINT fk_ppl_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ppl_lista FOREIGN KEY (id_lista) REFERENCES listas_precios(id_lista) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_ppl_precio CHECK (precio_unitario_neto > 0)
);

CREATE TABLE historico_precios (
  id_historico BIGINT NOT NULL AUTO_INCREMENT,
  id_precio INT NOT NULL,
  id_producto INT NOT NULL,
  id_lista INT NOT NULL,
  precio_anterior BIGINT NOT NULL,
  precio_nuevo BIGINT NOT NULL,
  fecha_cambio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_empleado_modifico INT DEFAULT NULL,
  PRIMARY KEY (id_historico),
  KEY fk_hp_precio (id_precio),
  KEY fk_hp_empleado (id_empleado_modifico),
  CONSTRAINT fk_hp_precio FOREIGN KEY (id_precio) REFERENCES precios_por_lista(id_precio) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_hp_empleado FOREIGN KEY (id_empleado_modifico) REFERENCES empleados(id_empleado) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_hp_valores CHECK (precio_anterior > 0 AND precio_nuevo > 0)
);

CREATE TABLE promociones (
  id_promocion BIGINT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT,
  tipo_promocion ENUM('DESCUENTO_PORCENTAJE','DESCUENTO_MONTO','PRECIO_FIJO','NXM','COMBO') DEFAULT NULL,
  valor_descuento BIGINT DEFAULT NULL,
  fecha_inicio DATE DEFAULT NULL,
  fecha_fin DATE DEFAULT NULL,
  hora_inicio TIME DEFAULT NULL,
  hora_fin TIME DEFAULT NULL,
  dias_semana JSON DEFAULT NULL,
  aplica_a ENUM('PRODUCTO','CATEGORIA','TOTAL_VENTA','ESTUDIANTE_GRADO') DEFAULT NULL,
  min_cantidad INT DEFAULT NULL,
  monto_minimo BIGINT DEFAULT NULL,
  max_usos_cliente INT DEFAULT NULL,
  max_usos_total INT DEFAULT NULL,
  usos_actuales INT DEFAULT 0,
  requiere_codigo TINYINT(1) DEFAULT 0,
  codigo_promocion VARCHAR(50) DEFAULT NULL,
  prioridad INT DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  usuario_creacion VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (id_promocion),
  UNIQUE KEY uk_promocion_codigo (codigo_promocion),
  KEY idx_promocion_activo (activo),
  KEY idx_promocion_fechas (fecha_inicio, fecha_fin),
  KEY idx_promocion_tipo (tipo_promocion),
  KEY idx_promocion_prioridad (prioridad)
);

CREATE TABLE productos_promocion (
  id_producto_promocion INT NOT NULL AUTO_INCREMENT,
  id_promocion BIGINT NOT NULL,
  id_producto INT NOT NULL,
  PRIMARY KEY (id_producto_promocion),
  UNIQUE KEY uk_promocion_producto (id_promocion, id_producto),
  KEY fk_pp_promocion (id_promocion),
  KEY fk_pp_producto (id_producto),
  CONSTRAINT fk_pp_promocion FOREIGN KEY (id_promocion) REFERENCES promociones(id_promocion) ON DELETE CASCADE,
  CONSTRAINT fk_pp_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

CREATE TABLE categorias_promocion (
  id_categoria_promocion INT NOT NULL AUTO_INCREMENT,
  id_promocion BIGINT NOT NULL,
  id_categoria INT NOT NULL,
  PRIMARY KEY (id_categoria_promocion),
  UNIQUE KEY uk_promocion_categoria (id_promocion, id_categoria),
  KEY fk_cp_promocion (id_promocion),
  KEY fk_cp_categoria (id_categoria),
  CONSTRAINT fk_cp_promocion FOREIGN KEY (id_promocion) REFERENCES promociones(id_promocion) ON DELETE CASCADE,
  CONSTRAINT fk_cp_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE
);

-- =========================================================
-- Tarjetas y autorizaciones
-- =========================================================
CREATE TABLE tarjetas (
  nro_tarjeta VARCHAR(20) NOT NULL,
  id_hijo INT DEFAULT NULL,
  saldo_actual BIGINT NOT NULL DEFAULT 0,
  estado ENUM('Activa','Bloqueada','Vencida') NOT NULL DEFAULT 'Activa',
  fecha_vencimiento DATE DEFAULT NULL,
  saldo_alerta BIGINT NOT NULL DEFAULT 0,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  tipo_autorizacion VARCHAR(20),
  permite_saldo_negativo TINYINT(1) NOT NULL DEFAULT 0,
  limite_credito BIGINT NOT NULL DEFAULT 0,
  notificar_saldo_bajo TINYINT(1) NOT NULL DEFAULT 1,
  ultima_notificacion_saldo DATETIME DEFAULT NULL,
  PRIMARY KEY (nro_tarjeta),
  UNIQUE KEY uk_tarjeta_hijo (id_hijo),
  KEY idx_tarjeta_estado (estado),
  KEY idx_tarjeta_tipo_aut (tipo_autorizacion, estado),
  CONSTRAINT fk_tarjeta_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_tarjeta_saldo_negativo CHECK (
    (permite_saldo_negativo = 1 AND saldo_actual >= -limite_credito)
    OR (permite_saldo_negativo <> 1 AND saldo_actual >= 0)
  ),
  CONSTRAINT chk_tarjeta_saldo_alerta CHECK (saldo_alerta >= 0)
);

CREATE TABLE tarjetas_autorizacion (
  id_tarjeta_autorizacion INT NOT NULL AUTO_INCREMENT,
  codigo_barra VARCHAR(50) NOT NULL,
  id_empleado INT DEFAULT NULL,
  tipo_autorizacion ENUM('ADMIN','SUPERVISOR','CAJERO') DEFAULT NULL,
  puede_anular_almuerzos TINYINT(1) NOT NULL DEFAULT 0,
  puede_anular_ventas TINYINT(1) NOT NULL DEFAULT 0,
  puede_anular_recargas TINYINT(1) NOT NULL DEFAULT 0,
  puede_modificar_precios TINYINT(1) NOT NULL DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_vencimiento DATE DEFAULT NULL,
  observaciones TEXT,
  PRIMARY KEY (id_tarjeta_autorizacion),
  UNIQUE KEY uk_ta_codigo_barra (codigo_barra),
  KEY fk_ta_empleado (id_empleado),
  KEY idx_ta_activo (activo),
  CONSTRAINT fk_ta_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE SET NULL
);

CREATE TABLE log_autorizaciones (
  id_log BIGINT NOT NULL AUTO_INCREMENT,
  id_tarjeta_autorizacion INT,
  codigo_barra VARCHAR(50),
  tipo_operacion ENUM('ANULAR_ALMUERZO','ANULAR_VENTA','ANULAR_RECARGA','MODIFICAR_PRECIO','OTRO'),
  id_registro_afectado BIGINT,
  descripcion TEXT,
  id_usuario INT,
  fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip_origen VARCHAR(45),
  resultado ENUM('EXITOSO','RECHAZADO','ERROR'),
  PRIMARY KEY (id_log),
  KEY fk_log_ta (id_tarjeta_autorizacion),
  KEY idx_log_fecha (fecha_hora),
  KEY idx_log_tipo (tipo_operacion),
  CONSTRAINT fk_log_ta FOREIGN KEY (id_tarjeta_autorizacion) REFERENCES tarjetas_autorizacion(id_tarjeta_autorizacion) ON DELETE CASCADE
);

-- =========================================================
-- Documentos tributarios y timbrados (corregido orden para referencias)
-- =========================================================
CREATE TABLE puntos_expedicion (
  id_punto INT NOT NULL AUTO_INCREMENT,
  codigo_establecimiento VARCHAR(3),
  codigo_punto_expedicion VARCHAR(3),
  descripcion_ubicacion VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_punto),
  UNIQUE KEY uk_punto_establecimiento (codigo_establecimiento, codigo_punto_expedicion)
);

CREATE TABLE timbrados (
  nro_timbrado INT NOT NULL,
  id_punto INT DEFAULT NULL,
  tipo_documento ENUM('Factura','Nota Credito','Recibo') DEFAULT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  nro_inicial INT DEFAULT NULL,
  nro_final INT DEFAULT NULL,
  es_electronico TINYINT(1) NOT NULL DEFAULT 0,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (nro_timbrado),
  KEY fk_timbrado_punto (id_punto),
  CONSTRAINT chk_timbrado_fechas CHECK (fecha_fin > fecha_inicio),
  CONSTRAINT chk_timbrado_rango CHECK (nro_final IS NULL OR nro_final > nro_inicial),
  CONSTRAINT fk_timbrado_punto FOREIGN KEY (id_punto) REFERENCES puntos_expedicion(id_punto) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE documentos_tributarios (
  id_documento BIGINT NOT NULL AUTO_INCREMENT,
  nro_timbrado INT NOT NULL,
  nro_secuencial INT NOT NULL,
  fecha_emision DATETIME NOT NULL,
  monto_total BIGINT NOT NULL,
  monto_exento BIGINT DEFAULT NULL,
  monto_gravado_5 BIGINT DEFAULT NULL,
  monto_iva_5 BIGINT DEFAULT NULL,
  monto_gravado_10 BIGINT DEFAULT NULL,
  monto_iva_10 BIGINT DEFAULT NULL,
  PRIMARY KEY (id_documento),
  UNIQUE KEY uk_documento_timbrado_seq (nro_timbrado, nro_secuencial),
  KEY idx_doc_fecha (fecha_emision),
  KEY idx_doc_timbrado (nro_timbrado),
  CONSTRAINT fk_doc_timbrado FOREIGN KEY (nro_timbrado) REFERENCES timbrados(nro_timbrado) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_doc_total CHECK (monto_total > 0),
  CONSTRAINT chk_doc_iva5 CHECK ((ABS((monto_iva_5 * 21) - monto_gravado_5) <= 1) OR (monto_gravado_5 = 0)),
  CONSTRAINT chk_doc_iva10 CHECK ((ABS((monto_iva_10 * 11) - monto_gravado_10) <= 1) OR (monto_gravado_10 = 0))
);

-- =========================================================
-- Operaciones de ventas y pagos
-- =========================================================
CREATE TABLE ventas (
  id_venta BIGINT NOT NULL AUTO_INCREMENT,
  nro_factura_venta BIGINT DEFAULT NULL,
  id_cliente INT DEFAULT NULL,
  id_hijo INT DEFAULT NULL,
  id_tipo_pago INT DEFAULT NULL,
  id_empleado_cajero INT DEFAULT NULL,
  fecha DATETIME NOT NULL,
  monto_total BIGINT NOT NULL,
  tipo_venta VARCHAR(20),
  autorizado_por INT DEFAULT NULL,
  motivo_credito TEXT,
  genera_factura_legal TINYINT(1) NOT NULL DEFAULT 0,
  saldo_pendiente BIGINT NOT NULL DEFAULT 0,
  estado_pago ENUM('PENDIENTE','PARCIAL','PAGADA') NOT NULL DEFAULT 'PENDIENTE',
  estado ENUM('PROCESADO','ANULADO') NOT NULL DEFAULT 'PROCESADO',
  PRIMARY KEY (id_venta),
  UNIQUE KEY uk_venta_documento (nro_factura_venta),
  KEY fk_venta_hijo (id_hijo),
  KEY fk_venta_tipo_pago (id_tipo_pago),
  KEY fk_venta_cliente_fecha (id_cliente, fecha),
  KEY fk_venta_cajero_fecha (id_empleado_cajero, fecha),
  KEY idx_ventas_estado_pago (estado_pago, fecha),
  KEY idx_ventas_fecha (fecha),
  KEY idx_ventas_monto (monto_total),
  CONSTRAINT fk_venta_documento FOREIGN KEY (nro_factura_venta) REFERENCES documentos_tributarios(id_documento) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_venta_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_venta_tipo_pago FOREIGN KEY (id_tipo_pago) REFERENCES tipos_pago(id_tipo_pago) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_venta_cajero FOREIGN KEY (id_empleado_cajero) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_venta_autorizado FOREIGN KEY (autorizado_por) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_venta_monto CHECK (monto_total > 0)
);

CREATE TABLE pagos_venta (
  id_pago_venta BIGINT NOT NULL AUTO_INCREMENT,
  id_venta BIGINT NOT NULL,
  id_medio_pago INT DEFAULT NULL,
  id_cierre BIGINT DEFAULT NULL,
  nro_tarjeta_usada VARCHAR(20) DEFAULT NULL,
  monto_aplicado BIGINT NOT NULL,
  referencia_transaccion VARCHAR(100),
  fecha_pago DATETIME NOT NULL,
  estado ENUM('PROCESADO','ANULADO') NOT NULL DEFAULT 'PROCESADO',
  PRIMARY KEY (id_pago_venta),
  KEY fk_pv_venta (id_venta),
  KEY fk_pv_medio (id_medio_pago),
  KEY fk_pv_cierre (id_cierre),
  KEY fk_pv_tarjeta (nro_tarjeta_usada),
  KEY idx_pv_fecha_medio (fecha_pago, id_medio_pago),
  CONSTRAINT fk_pv_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pv_medio FOREIGN KEY (id_medio_pago) REFERENCES medios_pago(id_medio_pago) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_pv_tarjeta FOREIGN KEY (nro_tarjeta_usada) REFERENCES tarjetas(nro_tarjeta) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_pv_monto CHECK (monto_aplicado > 0)
);

CREATE TABLE aplicacion_pagos_ventas (
  id_aplicacion BIGINT NOT NULL AUTO_INCREMENT,
  id_pago_venta BIGINT DEFAULT NULL,
  id_venta BIGINT DEFAULT NULL,
  monto_aplicado BIGINT NOT NULL,
  fecha_aplicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_aplicacion),
  KEY fk_apv_pago (id_pago_venta),
  KEY fk_apv_venta (id_venta),
  CONSTRAINT fk_apv_pago FOREIGN KEY (id_pago_venta) REFERENCES pagos_venta(id_pago_venta) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_apv_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_apv_monto CHECK (monto_aplicado > 0)
);

CREATE TABLE detalle_venta (
  id_detalle BIGINT NOT NULL AUTO_INCREMENT,
  id_venta BIGINT DEFAULT NULL,
  id_producto INT DEFAULT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  precio_unitario BIGINT NOT NULL,
  subtotal_total BIGINT NOT NULL,
  PRIMARY KEY (id_detalle),
  UNIQUE KEY uk_venta_producto (id_venta, id_producto),
  KEY fk_dv_producto (id_producto),
  KEY fk_dv_venta (id_venta),
  CONSTRAINT fk_dv_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_dv_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_dv_valores CHECK (cantidad > 0 AND precio_unitario > 0 AND subtotal_total > 0)
);

-- =========================================================
-- Compras y pagos a proveedores
-- =========================================================
CREATE TABLE proveedores (
  id_proveedor INT NOT NULL AUTO_INCREMENT,
  ruc VARCHAR(20) NOT NULL,
  razon_social VARCHAR(255) NOT NULL,
  telefono VARCHAR(20),
  email VARCHAR(100),
  direccion VARCHAR(255),
  ciudad VARCHAR(100),
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_proveedor),
  UNIQUE KEY uk_proveedores_ruc (ruc)
);

CREATE TABLE compras (
  id_compra BIGINT NOT NULL AUTO_INCREMENT,
  id_proveedor INT DEFAULT NULL,
  fecha DATETIME NOT NULL,
  monto_total BIGINT NOT NULL,
  nro_factura VARCHAR(50),
  observaciones TEXT,
  saldo_pendiente BIGINT NOT NULL,
  estado_pago ENUM('PENDIENTE','PARCIAL','PAGADA') NOT NULL DEFAULT 'PENDIENTE',
  PRIMARY KEY (id_compra),
  KEY fk_compra_proveedor_fecha (id_proveedor, fecha),
  CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_compra_monto CHECK (monto_total > 0)
);

CREATE TABLE pagos_proveedores (
  id_pago_proveedor BIGINT NOT NULL AUTO_INCREMENT,
  id_proveedor INT DEFAULT NULL,
  numero_comprobante VARCHAR(20) DEFAULT NULL,
  fecha DATE NOT NULL,
  monto_total BIGINT NOT NULL,
  id_medio_pago INT DEFAULT NULL,
  observacion VARCHAR(255),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_pago_proveedor),
  UNIQUE KEY uk_pago_proveedor_comprobante (numero_comprobante),
  KEY fk_pp_proveedor (id_proveedor),
  KEY fk_pp_medio (id_medio_pago),
  KEY idx_pp_fecha (fecha),
  CONSTRAINT fk_pp_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_pp_medio FOREIGN KEY (id_medio_pago) REFERENCES medios_pago(id_medio_pago) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_pp_monto CHECK (monto_total > 0)
);

CREATE TABLE aplicacion_pagos_compras (
  id_aplicacion BIGINT NOT NULL AUTO_INCREMENT,
  id_pago_proveedor BIGINT DEFAULT NULL,
  id_compra BIGINT DEFAULT NULL,
  monto_aplicado BIGINT NOT NULL,
  fecha_aplicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_aplicacion),
  KEY fk_apc_pago (id_pago_proveedor),
  KEY fk_apc_compra (id_compra),
  CONSTRAINT fk_apc_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_apc_pago FOREIGN KEY (id_pago_proveedor) REFERENCES pagos_proveedores(id_pago_proveedor) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_apc_monto CHECK (monto_aplicado > 0)
);

CREATE TABLE detalle_compra (
  id_detalle BIGINT NOT NULL AUTO_INCREMENT,
  id_compra BIGINT DEFAULT NULL,
  id_producto INT DEFAULT NULL,
  costo_unitario_neto BIGINT NOT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  subtotal_neto BIGINT NOT NULL,
  monto_iva BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY (id_detalle),
  UNIQUE KEY uk_compra_producto (id_compra, id_producto),
  KEY fk_dc_producto (id_producto),
  CONSTRAINT fk_dc_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_dc_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_dc_valores CHECK (cantidad > 0 AND costo_unitario_neto > 0 AND subtotal_neto > 0)
);

-- =========================================================
-- Notas de crédito
-- =========================================================
CREATE TABLE notas_credito_cliente (
  id_nota BIGINT NOT NULL AUTO_INCREMENT,
  nro_factura_venta BIGINT DEFAULT NULL,
  id_cliente INT DEFAULT NULL,
  id_venta_original BIGINT DEFAULT NULL,
  fecha DATETIME NOT NULL,
  monto_total BIGINT NOT NULL,
  observacion VARCHAR(255),
  estado ENUM('Emitida','Aplicada','Anulada') NOT NULL DEFAULT 'Emitida',
  PRIMARY KEY (id_nota),
  UNIQUE KEY uk_nota_doc (nro_factura_venta),
  KEY fk_nota_cliente (id_cliente),
  KEY fk_nota_venta (id_venta_original),
  CONSTRAINT fk_nota_doc FOREIGN KEY (nro_factura_venta) REFERENCES documentos_tributarios(id_documento) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_nota_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_nota_venta FOREIGN KEY (id_venta_original) REFERENCES ventas(id_venta) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_nota_monto CHECK (monto_total > 0)
);

-- =========================================================
-- Cargas de saldo y consumos
-- =========================================================
CREATE TABLE cargas_saldo (
  id_carga BIGINT NOT NULL AUTO_INCREMENT,
  nro_tarjeta VARCHAR(20) NOT NULL,
  id_cliente_origen INT DEFAULT NULL,
  id_nota BIGINT DEFAULT NULL,
  fecha_carga DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  monto_cargado BIGINT NOT NULL,
  referencia VARCHAR(100),
  estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
  pay_request_id VARCHAR(100),
  fecha_confirmacion DATETIME DEFAULT NULL,
  custom_identifier VARCHAR(100),
  tx_id VARCHAR(100),
  PRIMARY KEY (id_carga),
  KEY fk_cs_cliente (id_cliente_origen),
  KEY fk_cs_nota (id_nota),
  KEY idx_cs_tarjeta_fecha (nro_tarjeta, fecha_carga),
  KEY idx_cs_tx (tx_id),
  KEY idx_cs_payreq (pay_request_id),
  CONSTRAINT fk_cs_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_cs_cliente FOREIGN KEY (id_cliente_origen) REFERENCES clientes(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_cs_nota FOREIGN KEY (id_nota) REFERENCES notas_credito_cliente(id_nota),
  CONSTRAINT chk_cs_monto CHECK (monto_cargado > 0)
);

CREATE TABLE consumos_tarjeta (
  id_consumo BIGINT NOT NULL AUTO_INCREMENT,
  nro_tarjeta VARCHAR(20) DEFAULT NULL,
  fecha_consumo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  monto_consumido BIGINT NOT NULL,
  detalle VARCHAR(200),
  saldo_anterior BIGINT DEFAULT NULL,
  saldo_posterior BIGINT DEFAULT NULL,
  id_empleado_registro INT DEFAULT NULL,
  PRIMARY KEY (id_consumo),
  KEY fk_ct_empleado (id_empleado_registro),
  KEY idx_ct_tarjeta_fecha (nro_tarjeta, fecha_consumo),
  KEY idx_ct_fecha (fecha_consumo),
  CONSTRAINT fk_ct_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON UPDATE CASCADE,
  CONSTRAINT fk_ct_empleado FOREIGN KEY (id_empleado_registro) REFERENCES empleados(id_empleado),
  CONSTRAINT chk_ct_monto CHECK (monto_consumido > 0)
);

-- =========================================================
-- Notas de crédito de proveedor
-- =========================================================

CREATE TABLE notas_credito_proveedor (
  id_nota_proveedor BIGINT NOT NULL AUTO_INCREMENT,
  nro_factura_compra BIGINT DEFAULT NULL,
  id_proveedor INT DEFAULT NULL,
  id_compra_original BIGINT DEFAULT NULL,
  fecha DATETIME NOT NULL,
  monto_total BIGINT NOT NULL,
  observacion VARCHAR(255),
  estado ENUM('EMITIDA','APLICADA','ANULADA') NOT NULL DEFAULT 'EMITIDA',
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_nota_proveedor),
  KEY fk_ncp_compra (id_compra_original),
  KEY fk_ncp_proveedor (id_proveedor),
  KEY idx_ncp_fecha (fecha),
  KEY idx_ncp_estado (estado),
  CONSTRAINT fk_ncp_compra FOREIGN KEY (id_compra_original) REFERENCES compras(id_compra) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_ncp_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_ncp_monto CHECK (monto_total > 0)
);

CREATE TABLE detalle_nota (
  id_detalle BIGINT NOT NULL AUTO_INCREMENT,
  id_nota BIGINT DEFAULT NULL,
  id_producto INT DEFAULT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  precio_unitario BIGINT NOT NULL,
  subtotal BIGINT NOT NULL,
  PRIMARY KEY (id_detalle),
  UNIQUE KEY uk_nota_producto (id_nota, id_producto),
  KEY fk_dn_producto (id_producto),
  CONSTRAINT fk_dn_nota FOREIGN KEY (id_nota) REFERENCES notas_credito_cliente(id_nota) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_dn_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_dn_valores CHECK (cantidad > 0 AND precio_unitario > 0 AND subtotal > 0)
);

CREATE TABLE detalle_nota_credito_proveedor (
  id_detalle_nc_proveedor BIGINT NOT NULL AUTO_INCREMENT,
  id_nota_proveedor BIGINT DEFAULT NULL,
  id_producto INT DEFAULT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  precio_unitario BIGINT NOT NULL,
  subtotal BIGINT NOT NULL,
  PRIMARY KEY (id_detalle_nc_proveedor),
  KEY fk_dncp_nota (id_nota_proveedor),
  KEY fk_dncp_producto (id_producto),
  CONSTRAINT fk_dncp_nota FOREIGN KEY (id_nota_proveedor) REFERENCES notas_credito_proveedor(id_nota_proveedor) ON DELETE CASCADE,
  CONSTRAINT fk_dncp_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT,
  CONSTRAINT chk_dncp_valores CHECK (cantidad > 0 AND precio_unitario >= 0 AND subtotal >= 0)
);

-- =========================================================
-- Datos de facturación (física y electrónica)
-- =========================================================
CREATE TABLE datos_facturacion_fisica (
  id_documento BIGINT NOT NULL,
  nro_preimpreso_interno VARCHAR(20),
  PRIMARY KEY (id_documento),
  UNIQUE KEY uk_preimpreso (nro_preimpreso_interno),
  CONSTRAINT fk_dff_doc FOREIGN KEY (id_documento) REFERENCES documentos_tributarios(id_documento) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE datos_facturacion_elect (
  id_documento BIGINT NOT NULL,
  cdc CHAR(44),
  url_kude VARCHAR(255),
  xml_transmitido TEXT,
  estado_sifen ENUM('Aprobado','Rechazado','Anulado','Pendiente','Cancelado') DEFAULT NULL,
  fecha_envio DATETIME DEFAULT NULL,
  fecha_respuesta DATETIME DEFAULT NULL,
  PRIMARY KEY (id_documento),
  UNIQUE KEY uk_dfe_cdc (cdc),
  CONSTRAINT fk_dfe_doc FOREIGN KEY (id_documento) REFERENCES documentos_tributarios(id_documento) ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================================================
-- Inventario y stock
-- =========================================================
CREATE TABLE stock_unico (
  id_producto INT NOT NULL,
  stock_actual DECIMAL(10,3) NOT NULL DEFAULT 0,
  fecha_ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_producto),
  KEY idx_stock_actual (stock_actual),
  CONSTRAINT fk_stock_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE movimientos_stock (
  id_movimiento_stock BIGINT NOT NULL AUTO_INCREMENT,
  id_producto INT NOT NULL,
  id_empleado_autoriza INT DEFAULT NULL,
  id_venta BIGINT DEFAULT NULL,
  id_compra BIGINT DEFAULT NULL,
  fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
  tipo_movimiento ENUM('Entrada','Salida','Ajuste') NOT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  stock_resultante DECIMAL(10,3) NOT NULL,
  referencia_documento VARCHAR(50),
  PRIMARY KEY (id_movimiento_stock),
  KEY fk_ms_empleado (id_empleado_autoriza),
  KEY fk_ms_venta (id_venta),
  KEY fk_ms_compra (id_compra),
  KEY idx_ms_producto_fecha (id_producto, fecha_hora),
  CONSTRAINT fk_ms_empleado FOREIGN KEY (id_empleado_autoriza) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_ms_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_ms_compra FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_ms_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_ms_cantidad CHECK (cantidad > 0)
);

CREATE TABLE ajustes_inventario (
  id_ajuste BIGINT NOT NULL AUTO_INCREMENT,
  id_empleado_responsable INT DEFAULT NULL,
  fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
  tipo_ajuste ENUM('Positivo','Negativo') DEFAULT NULL,
  motivo VARCHAR(255),
  estado ENUM('Borrador','Finalizado') DEFAULT 'Borrador',
  PRIMARY KEY (id_ajuste),
  KEY fk_ai_empleado (id_empleado_responsable),
  CONSTRAINT fk_ai_empleado FOREIGN KEY (id_empleado_responsable) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE detalle_ajuste (
  id_detalle BIGINT NOT NULL AUTO_INCREMENT,
  id_ajuste BIGINT DEFAULT NULL,
  id_producto INT DEFAULT NULL,
  id_movimiento_stock BIGINT DEFAULT NULL,
  cantidad_ajustada DECIMAL(8,3) DEFAULT NULL,
  PRIMARY KEY (id_detalle),
  UNIQUE KEY uk_detalle_mov (id_movimiento_stock),
  UNIQUE KEY uk_ajuste_producto (id_ajuste, id_producto),
  KEY fk_da_producto (id_producto),
  CONSTRAINT fk_da_ajuste FOREIGN KEY (id_ajuste) REFERENCES ajustes_inventario(id_ajuste) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_da_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- =========================================================
-- Almuerzos / planes / suscripciones / cuentas
-- =========================================================
CREATE TABLE planes_almuerzo (
  id_plan_almuerzo INT NOT NULL AUTO_INCREMENT,
  nombre_plan VARCHAR(100) NOT NULL,
  descripcion TEXT,
  precio_mensual BIGINT NOT NULL,
  dias_semana_incluidos VARCHAR(60),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_plan_almuerzo),
  UNIQUE KEY uk_plan_nombre (nombre_plan),
  CONSTRAINT chk_plan_precio CHECK (precio_mensual > 0)
);

CREATE TABLE tipos_almuerzo (
  id_tipo_almuerzo INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  precio_unitario BIGINT NOT NULL,
  incluye_plato_principal TINYINT(1) DEFAULT 0,
  incluye_postre TINYINT(1) DEFAULT 0,
  incluye_bebida TINYINT(1) DEFAULT 0,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_tipo_almuerzo),
  KEY idx_ta_activo (activo),
  CONSTRAINT chk_ta_precio CHECK (precio_unitario > 0)
);

CREATE TABLE suscripciones_almuerzo (
  id_suscripcion BIGINT NOT NULL AUTO_INCREMENT,
  id_hijo INT DEFAULT NULL,
  id_plan_almuerzo INT DEFAULT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE DEFAULT NULL,
  estado ENUM('Activa','Pendiente','Cancelada','Vencida') NOT NULL DEFAULT 'Activa',
  PRIMARY KEY (id_suscripcion),
  UNIQUE KEY uk_suscripcion_activa (id_hijo, id_plan_almuerzo, estado),
  KEY fk_sa_plan (id_plan_almuerzo),
  CONSTRAINT fk_sa_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_sa_plan FOREIGN KEY (id_plan_almuerzo) REFERENCES planes_almuerzo(id_plan_almuerzo) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_sa_fechas CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE TABLE cuentas_almuerzo_mensual (
  id_cuenta BIGINT NOT NULL AUTO_INCREMENT,
  id_hijo INT DEFAULT NULL,
  anio INT DEFAULT NULL,
  mes TINYINT DEFAULT NULL,
  cantidad_almuerzos INT NOT NULL DEFAULT 0,
  monto_total BIGINT NOT NULL DEFAULT 0,
  forma_cobro ENUM('CONTADO_ANTICIPADO','CREDITO_MENSUAL') DEFAULT 'CONTADO_ANTICIPADO',
  monto_pagado BIGINT NOT NULL DEFAULT 0,
  estado ENUM('PENDIENTE','PARCIAL','PAGADO') NOT NULL DEFAULT 'PENDIENTE',
  fecha_generacion DATE DEFAULT CURRENT_DATE,
  fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  observaciones TEXT,
  PRIMARY KEY (id_cuenta),
  UNIQUE KEY uk_cuenta_mes (id_hijo, anio, mes),
  KEY idx_cam_estado (estado),
  KEY idx_cam_fecha (fecha_generacion),
  CONSTRAINT fk_cam_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo),
  CONSTRAINT chk_cam_mes CHECK (mes BETWEEN 1 AND 12)
);

CREATE TABLE pagos_cuentas_almuerzo (
  id_pago BIGINT NOT NULL AUTO_INCREMENT,
  id_cuenta BIGINT DEFAULT NULL,
  fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
  medio_pago ENUM('EFECTIVO','DEBITO','CREDITO','TRANSFERENCIA','OTRO') DEFAULT 'EFECTIVO',
  monto BIGINT NOT NULL,
  referencia VARCHAR(50),
  observaciones TEXT,
  id_empleado_registro INT DEFAULT NULL,
  PRIMARY KEY (id_pago),
  KEY fk_pca_empleado (id_empleado_registro),
  KEY fk_pca_cuenta (id_cuenta),
  CONSTRAINT fk_pca_cuenta FOREIGN KEY (id_cuenta) REFERENCES cuentas_almuerzo_mensual(id_cuenta),
  CONSTRAINT fk_pca_empleado FOREIGN KEY (id_empleado_registro) REFERENCES empleados(id_empleado),
  CONSTRAINT chk_pca_monto CHECK (monto > 0)
);

CREATE TABLE pagos_almuerzo_mensual (
  id_pago_almuerzo BIGINT NOT NULL AUTO_INCREMENT,
  id_suscripcion BIGINT DEFAULT NULL,
  fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
  monto_pagado BIGINT NOT NULL,
  mes_pagado DATE NOT NULL,
  id_venta BIGINT DEFAULT NULL,
  estado ENUM('Pagado','Pendiente','Anulado') DEFAULT 'Pagado',
  PRIMARY KEY (id_pago_almuerzo),
  UNIQUE KEY uk_pam_mes (id_suscripcion, mes_pagado),
  UNIQUE KEY uk_pam_venta (id_venta),
  CONSTRAINT fk_pam_suscripcion FOREIGN KEY (id_suscripcion) REFERENCES suscripciones_almuerzo(id_suscripcion) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_pam_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_pam_monto CHECK (monto_pagado > 0)
);

CREATE TABLE registro_consumo_almuerzo (
  id_registro_consumo BIGINT NOT NULL AUTO_INCREMENT,
  id_hijo INT DEFAULT NULL,
  nro_tarjeta VARCHAR(20) DEFAULT NULL,
  id_tipo_almuerzo INT DEFAULT NULL,
  costo_almuerzo BIGINT DEFAULT NULL,
  marcado_en_cuenta TINYINT(1) DEFAULT 0,
  fecha_consumo DATE DEFAULT NULL,
  id_suscripcion BIGINT DEFAULT NULL,
  hora_registro TIME DEFAULT NULL,
  PRIMARY KEY (id_registro_consumo),
  UNIQUE KEY uk_consumo_dia (id_hijo, fecha_consumo),
  KEY fk_rca_suscripcion (id_suscripcion),
  KEY fk_rca_tarjeta (nro_tarjeta),
  KEY fk_rca_tipo (id_tipo_almuerzo),
  KEY idx_rca_marcado (marcado_en_cuenta, fecha_consumo),
  KEY idx_rca_fecha_hijo (fecha_consumo, id_hijo),
  CONSTRAINT fk_rca_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON UPDATE CASCADE,
  CONSTRAINT fk_rca_tipo FOREIGN KEY (id_tipo_almuerzo) REFERENCES tipos_almuerzo(id_tipo_almuerzo),
  CONSTRAINT fk_rca_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_rca_suscripcion FOREIGN KEY (id_suscripcion) REFERENCES suscripciones_almuerzo(id_suscripcion) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- =========================================================
-- Restricciones / alérgenos (modelo relacional)
-- =========================================================
CREATE TABLE restricciones_hijos (
  id_restriccion INT NOT NULL AUTO_INCREMENT,
  id_hijo INT DEFAULT NULL,
  tipo_restriccion VARCHAR(100) DEFAULT NULL,
  descripcion TEXT,
  observaciones TEXT,
  severidad ENUM('Leve','Moderada','Severa','Crítica') DEFAULT 'Moderada',
  requiere_autorizacion TINYINT(1) DEFAULT 0,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  activo TINYINT(1) DEFAULT 1,
  PRIMARY KEY (id_restriccion),
  KEY idx_rh_hijo (id_hijo),
  KEY idx_rh_tipo (tipo_restriccion),
  KEY idx_rh_activo (activo),
  CONSTRAINT fk_rh_hijo FOREIGN KEY (id_hijo) REFERENCES hijos(id_hijo) ON DELETE CASCADE
);

CREATE TABLE producto_alergenos (
  id_producto_alergeno INT NOT NULL AUTO_INCREMENT,
  id_producto INT DEFAULT NULL,
  id_alergeno INT DEFAULT NULL,
  contiene TINYINT(1) DEFAULT 1,
  observaciones TEXT,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
  usuario_registro VARCHAR(100),
  PRIMARY KEY (id_producto_alergeno),
  UNIQUE KEY uk_producto_alergeno (id_producto, id_alergeno),
  KEY idx_pa_producto (id_producto),
  KEY idx_pa_alergeno (id_alergeno),
  CONSTRAINT fk_pa_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
  CONSTRAINT fk_pa_alergeno FOREIGN KEY (id_alergeno) REFERENCES alergenos(id_alergeno) ON DELETE CASCADE
);

-- =========================================================
-- Seguridad / auditoría mínima (complementaria a Django)
-- =========================================================
CREATE TABLE usuarios_web_clientes (
  id_cliente INT NOT NULL,
  usuario VARCHAR(50) NOT NULL,
  contrasena_hash VARCHAR(128),
  ultimo_acceso DATETIME DEFAULT NULL,
  activo TINYINT(1) DEFAULT 1,
  PRIMARY KEY (id_cliente),
  UNIQUE KEY uk_uwc_usuario (usuario),
  CONSTRAINT fk_uwc_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE usuario_portal (
  id_usuario_portal INT NOT NULL AUTO_INCREMENT,
  id_cliente INT NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email_verificado TINYINT(1) NOT NULL DEFAULT 0,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso DATETIME DEFAULT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usuario_portal),
  UNIQUE KEY uk_up_email (email),
  KEY idx_up_cliente (id_cliente),
  CONSTRAINT fk_up_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

CREATE TABLE tokens_recuperacion (
  id_token INT NOT NULL AUTO_INCREMENT,
  id_cliente INT NOT NULL,
  token VARCHAR(64) NOT NULL,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_expiracion DATETIME NOT NULL,
  usado TINYINT(1) NOT NULL DEFAULT 0,
  fecha_uso DATETIME DEFAULT NULL,
  ip_solicitud VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (id_token),
  UNIQUE KEY uk_tr_token (token),
  KEY idx_tr_cliente (id_cliente),
  KEY idx_tr_expiracion (fecha_expiracion),
  CONSTRAINT fk_tr_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE token_verificacion (
  id_token INT NOT NULL AUTO_INCREMENT,
  id_usuario_portal INT NOT NULL,
  token VARCHAR(64) NOT NULL,
  tipo ENUM('email_verification','password_reset') NOT NULL,
  expira_en DATETIME NOT NULL,
  usado TINYINT(1) NOT NULL DEFAULT 0,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_token),
  UNIQUE KEY uk_tv_token (token),
  KEY idx_tv_usuario (id_usuario_portal),
  KEY idx_tv_tipo (tipo),
  KEY idx_tv_expira (expira_en),
  CONSTRAINT fk_tv_usuario FOREIGN KEY (id_usuario_portal) REFERENCES usuario_portal(id_usuario_portal) ON DELETE CASCADE
);

CREATE TABLE tokens_verificacion (
  id_token INT NOT NULL AUTO_INCREMENT,
  id_usuario_portal INT NOT NULL,
  token VARCHAR(100) NOT NULL,
  tipo VARCHAR(50) NOT NULL,
  expira_en DATETIME NOT NULL,
  usado TINYINT(1) DEFAULT 0,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_uso DATETIME DEFAULT NULL,
  PRIMARY KEY (id_token),
  UNIQUE KEY uk_tksv_token (token),
  KEY idx_tksv_usuario (id_usuario_portal),
  CONSTRAINT fk_tksv_usuario FOREIGN KEY (id_usuario_portal) REFERENCES usuario_portal(id_usuario_portal) ON DELETE CASCADE
);

CREATE TABLE auditoria_usuarios_web (
  id_auditoria BIGINT NOT NULL AUTO_INCREMENT,
  id_cliente INT DEFAULT NULL,
  fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
  campo_modificado VARCHAR(50),
  valor_anterior TEXT,
  valor_nuevo TEXT,
  ip_origen VARCHAR(45),
  PRIMARY KEY (id_auditoria),
  KEY fk_auw_cliente (id_cliente),
  CONSTRAINT fk_auw_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL
);

CREATE TABLE auditoria_operaciones (
  id_auditoria INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100) NOT NULL,
  tipo_usuario ENUM('EMPLEADO','CLIENTE_WEB','ADMIN') NOT NULL,
  id_usuario INT DEFAULT NULL,
  operacion VARCHAR(100) NOT NULL,
  tabla_afectada VARCHAR(100),
  id_registro INT DEFAULT NULL,
  descripcion TEXT,
  datos_anteriores JSON,
  datos_nuevos JSON,
  ip_address VARCHAR(45),
  ciudad VARCHAR(100),
  pais VARCHAR(100),
  user_agent TEXT,
  fecha_operacion DATETIME NOT NULL,
  resultado ENUM('EXITOSO','FALLIDO') NOT NULL,
  mensaje_error TEXT,
  PRIMARY KEY (id_auditoria),
  KEY idx_ao_usuario (usuario),
  KEY idx_ao_fecha (fecha_operacion),
  KEY idx_ao_operacion (operacion),
  KEY idx_ao_tabla (tabla_afectada, id_registro)
);

-- =========================================================
-- Alertas / métricas / seguridad
-- =========================================================
CREATE TABLE alertas_sistema (
  id_alerta BIGINT NOT NULL AUTO_INCREMENT,
  tipo ENUM('STOCK_MINIMO','SALDO_BAJO','LIMITE_CREDITO','TIMBRADO_VENCIDO','TARJETA_VENCIDA','SISTEMA') DEFAULT NULL,
  mensaje VARCHAR(500),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_leida DATETIME DEFAULT NULL,
  estado ENUM('Pendiente','Leida','Resuelta') DEFAULT 'Pendiente',
  id_empleado_resuelve INT DEFAULT NULL,
  fecha_resolucion DATETIME DEFAULT NULL,
  observaciones TEXT,
  PRIMARY KEY (id_alerta),
  KEY fk_alerta_empleado (id_empleado_resuelve),
  CONSTRAINT fk_alerta_empleado FOREIGN KEY (id_empleado_resuelve) REFERENCES empleados(id_empleado) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE metricas_rendimiento (
  id_metrica BIGINT NOT NULL AUTO_INCREMENT,
  fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
  tipo_metrica ENUM('ESPACIO','CONEXIONES','CONSULTAS_LENTAS','ERRORES') DEFAULT NULL,
  nombre_metrica VARCHAR(100),
  valor DECIMAL(15,2),
  unidad VARCHAR(20),
  umbral_alerta DECIMAL(15,2),
  estado ENUM('NORMAL','ADVERTENCIA','CRITICO') DEFAULT 'NORMAL',
  PRIMARY KEY (id_metrica),
  KEY idx_mr_fecha_tipo (fecha_hora, tipo_metrica),
  KEY idx_mr_estado (estado)
);

CREATE TABLE anomalias_detectadas (
  id_anomalia INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100),
  tipo_anomalia ENUM('IP_NUEVA','HORARIO_INUSUAL','MULTIPLES_SESIONES','UBICACION_SOSPECHOSA'),
  ip_address VARCHAR(45),
  fecha_deteccion DATETIME DEFAULT CURRENT_TIMESTAMP,
  descripcion TEXT,
  nivel_riesgo ENUM('BAJO','MEDIO','ALTO'),
  notificado TINYINT(1) DEFAULT 0,
  PRIMARY KEY (id_anomalia),
  KEY idx_anomalia_usuario (usuario),
  KEY idx_anomalia_tipo (tipo_anomalia),
  KEY idx_anomalia_fecha (fecha_deteccion),
  KEY idx_anomalia_notificado (notificado)
);

CREATE TABLE bloqueos_cuenta (
  id_bloqueo INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100),
  tipo_usuario ENUM('EMPLEADO','CLIENTE_WEB','ADMIN'),
  motivo VARCHAR(200),
  fecha_bloqueo DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_desbloqueo DATETIME DEFAULT NULL,
  ip_address VARCHAR(45),
  activo TINYINT(1) DEFAULT 1,
  bloqueado_por VARCHAR(100),
  PRIMARY KEY (id_bloqueo),
  KEY idx_bloqueo_usuario_activo (usuario, activo),
  KEY idx_bloqueo_fecha_desbloqueo (fecha_desbloqueo)
);

CREATE TABLE intentos_login (
  id_intento INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100),
  ip_address VARCHAR(45),
  ciudad VARCHAR(100),
  pais VARCHAR(100),
  fecha_intento DATETIME DEFAULT CURRENT_TIMESTAMP,
  exitoso TINYINT(1) DEFAULT 0,
  motivo_fallo VARCHAR(100),
  PRIMARY KEY (id_intento),
  KEY idx_login_usuario_fecha (usuario, fecha_intento),
  KEY idx_login_ip_fecha (ip_address, fecha_intento)
);

CREATE TABLE autenticacion_2fa (
  id_2fa INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100) NOT NULL,
  tipo_usuario ENUM('ADMIN','CAJERO','CLIENTE_WEB') NOT NULL,
  secret_key VARCHAR(32) NOT NULL,
  backup_codes TEXT,
  habilitado TINYINT(1) DEFAULT 0,
  fecha_activacion DATETIME DEFAULT NULL,
  ultima_verificacion DATETIME DEFAULT NULL,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_2fa),
  UNIQUE KEY uk_2fa_usuario_tipo (usuario, tipo_usuario),
  KEY idx_2fa_habilitado (habilitado)
);

CREATE TABLE intentos_2fa (
  id_intento INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100) NOT NULL,
  tipo_usuario ENUM('ADMIN','CAJERO','CLIENTE_WEB') NOT NULL,
  ip_address VARCHAR(45),
  ciudad VARCHAR(100),
  pais VARCHAR(100),
  codigo_ingresado VARCHAR(10),
  exitoso TINYINT(1) DEFAULT 0,
  tipo_codigo ENUM('TOTP','BACKUP') DEFAULT NULL,
  fecha_intento DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_intento),
  KEY idx_2fa_usuario (usuario),
  KEY idx_2fa_fecha (fecha_intento),
  KEY idx_2fa_exitoso (exitoso)
);

CREATE TABLE patrones_acceso (
  id_patron INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100),
  tipo_usuario ENUM('EMPLEADO','CLIENTE_WEB','ADMIN'),
  ip_address VARCHAR(45),
  horario_inicio TIME,
  horario_fin TIME,
  dias_semana VARCHAR(50),
  primera_deteccion DATETIME DEFAULT NULL,
  ultima_deteccion DATETIME DEFAULT NULL,
  frecuencia_accesos INT DEFAULT NULL,
  es_habitual TINYINT(1) DEFAULT 0,
  PRIMARY KEY (id_patron),
  KEY idx_patron_usuario (usuario),
  KEY idx_patron_ip (ip_address),
  KEY idx_patron_habitual (es_habitual)
);

CREATE TABLE restricciones_horarias (
  id_restriccion INT NOT NULL AUTO_INCREMENT,
  usuario VARCHAR(100) DEFAULT NULL,
  tipo_usuario ENUM('ADMIN','CAJERO','CLIENTE_WEB') NOT NULL,
  dia_semana ENUM('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO') NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  activo TINYINT(1) DEFAULT 1,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_restriccion),
  KEY idx_rh_usuario (usuario),
  KEY idx_rh_tipo_usuario (tipo_usuario),
  KEY idx_rh_activo (activo)
);

-- =========================================================
-- Notificaciones
-- =========================================================
CREATE TABLE notificacion (
  id_notificacion INT NOT NULL AUTO_INCREMENT,
  id_usuario_portal INT DEFAULT NULL,
  tipo VARCHAR(50),
  titulo VARCHAR(255),
  mensaje TEXT,
  leida TINYINT(1) DEFAULT 0,
  fecha_envio DATETIME DEFAULT NULL,
  fecha_lectura DATETIME DEFAULT NULL,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_notificacion),
  KEY idx_notif_usuario (id_usuario_portal),
  KEY idx_notif_tipo (tipo),
  KEY idx_notif_leida (leida),
  KEY idx_notif_fecha_envio (fecha_envio),
  CONSTRAINT fk_notif_usuario FOREIGN KEY (id_usuario_portal) REFERENCES usuario_portal(id_usuario_portal) ON DELETE CASCADE
);

CREATE TABLE notificacion_saldo (
  id_notificacion BIGINT NOT NULL AUTO_INCREMENT,
  nro_tarjeta VARCHAR(20) NOT NULL,
  tipo_notificacion VARCHAR(50) NOT NULL,
  saldo_actual BIGINT NOT NULL,
  mensaje TEXT NOT NULL,
  enviada_email TINYINT(1) DEFAULT 0,
  enviada_sms TINYINT(1) DEFAULT 0,
  leida TINYINT(1) DEFAULT 0,
  email_destinatario VARCHAR(255),
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_envio DATETIME DEFAULT NULL,
  PRIMARY KEY (id_notificacion),
  KEY idx_notif_tarjeta_tipo (nro_tarjeta, tipo_notificacion),
  KEY idx_notif_leida2 (leida),
  KEY idx_notif_fecha_creacion (fecha_creacion),
  CONSTRAINT fk_notif_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON DELETE CASCADE
);

CREATE TABLE solicitudes_notificacion (
  id_solicitud BIGINT NOT NULL AUTO_INCREMENT,
  id_cliente INT DEFAULT NULL,
  nro_tarjeta VARCHAR(20) DEFAULT NULL,
  saldo_alerta BIGINT DEFAULT NULL,
  mensaje VARCHAR(255),
  destino ENUM('SMS','WhatsApp','Email') DEFAULT 'Email',
  estado ENUM('Pendiente','Enviado','Error') DEFAULT 'Pendiente',
  fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_envio DATETIME DEFAULT NULL,
  PRIMARY KEY (id_solicitud),
  KEY fk_sol_cliente (id_cliente),
  KEY fk_sol_tarjeta (nro_tarjeta),
  CONSTRAINT fk_sol_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_sol_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE preferencia_notificacion (
  id_preferencia INT NOT NULL AUTO_INCREMENT,
  id_usuario_portal INT DEFAULT NULL,
  tipo_notificacion VARCHAR(50) DEFAULT NULL,
  email_activo TINYINT(1) DEFAULT 1,
  push_activo TINYINT(1) DEFAULT 0,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_preferencia),
  UNIQUE KEY uk_pref_usuario_tipo (id_usuario_portal, tipo_notificacion),
  KEY idx_pref_usuario (id_usuario_portal),
  KEY idx_pref_tipo (tipo_notificacion),
  CONSTRAINT fk_pref_usuario FOREIGN KEY (id_usuario_portal) REFERENCES usuario_portal(id_usuario_portal) ON DELETE CASCADE
);

-- =========================================================
-- Cajas / cierres
-- =========================================================
CREATE TABLE cajas (
  id_caja INT NOT NULL AUTO_INCREMENT,
  nombre_caja VARCHAR(50),
  ubicacion VARCHAR(100),
  activo TINYINT(1) DEFAULT 1,
  PRIMARY KEY (id_caja)
);

CREATE TABLE cierres_caja (
  id_cierre BIGINT NOT NULL AUTO_INCREMENT,
  id_caja INT DEFAULT NULL,
  id_empleado INT DEFAULT NULL,
  fecha_hora_apertura DATETIME DEFAULT NULL,
  fecha_hora_cierre DATETIME DEFAULT NULL,
  monto_inicial BIGINT DEFAULT 0,
  monto_contado_fisico BIGINT DEFAULT NULL,
  diferencia_efectivo BIGINT DEFAULT NULL,
  estado ENUM('Abierto','Cerrado') DEFAULT 'Abierto',
  PRIMARY KEY (id_cierre),
  KEY fk_cc_caja (id_caja),
  KEY fk_cc_empleado (id_empleado),
  CONSTRAINT fk_cc_caja FOREIGN KEY (id_caja) REFERENCES cajas(id_caja) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_cc_empleado FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_cc_fechas CHECK (fecha_hora_cierre IS NULL OR fecha_hora_cierre >= fecha_hora_apertura)
);

-- =========================================================
-- Autorización saldo negativo
-- =========================================================
CREATE TABLE autorizacion_saldo_negativo (
  id_autorizacion BIGINT NOT NULL AUTO_INCREMENT,
  id_venta BIGINT NOT NULL,
  nro_tarjeta VARCHAR(20) NOT NULL,
  id_empleado_autoriza INT NOT NULL,
  saldo_anterior BIGINT NOT NULL,
  monto_venta BIGINT NOT NULL,
  saldo_resultante BIGINT NOT NULL,
  motivo VARCHAR(255) NOT NULL,
  fecha_autorizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_regularizacion DATETIME DEFAULT NULL,
  id_carga_regularizacion BIGINT DEFAULT NULL,
  regularizado TINYINT(1) DEFAULT 0,
  PRIMARY KEY (id_autorizacion),
  KEY fk_asn_venta (id_venta),
  KEY fk_asn_carga (id_carga_regularizacion),
  KEY idx_asn_tarjeta_fecha (nro_tarjeta, fecha_autorizacion),
  KEY idx_asn_regularizado (regularizado),
  KEY idx_asn_empleado (id_empleado_autoriza),
  CONSTRAINT fk_asn_carga FOREIGN KEY (id_carga_regularizacion) REFERENCES cargas_saldo(id_carga) ON DELETE SET NULL,
  CONSTRAINT fk_asn_empleado FOREIGN KEY (id_empleado_autoriza) REFERENCES empleados(id_empleado) ON DELETE RESTRICT,
  CONSTRAINT fk_asn_tarjeta FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta) ON DELETE CASCADE,
  CONSTRAINT fk_asn_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE RESTRICT
);

-- =========================================================
-- Otros catálogos / soporte
-- =========================================================
CREATE TABLE tipos_almuerzo_grado (
  id_grado INT NOT NULL AUTO_INCREMENT,
  nombre_grado VARCHAR(50),
  nivel INT,
  orden_visualizacion INT,
  es_ultimo_grado TINYINT(1) DEFAULT 0,
  activo TINYINT(1) DEFAULT 1,
  fecha_creacion TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_grado),
  UNIQUE KEY uk_grado_nombre (nombre_grado),
  KEY idx_grado_nivel (nivel),
  KEY idx_grado_activo (activo)
);

-- =========================================================
-- Procedimientos y triggers principales (ajustados)
-- =========================================================
DELIMITER //

CREATE TRIGGER trg_crear_stock_unico AFTER INSERT ON productos
FOR EACH ROW
BEGIN
  INSERT INTO stock_unico (id_producto, stock_actual, fecha_ultima_actualizacion)
  VALUES (NEW.id_producto, 0, NOW());
END//

CREATE TRIGGER trg_carga_suma_saldo AFTER INSERT ON cargas_saldo
FOR EACH ROW
BEGIN
  UPDATE tarjetas
     SET saldo_actual = saldo_actual + NEW.monto_cargado
   WHERE nro_tarjeta = NEW.nro_tarjeta;
END//

CREATE TRIGGER trg_consumo_resta_saldo BEFORE INSERT ON consumos_tarjeta
FOR EACH ROW
BEGIN
  DECLARE v_saldo BIGINT;
  DECLARE v_perm TINYINT;
  DECLARE v_lim BIGINT;

  SELECT saldo_actual, permite_saldo_negativo, limite_credito
    INTO v_saldo, v_perm, v_lim
    FROM tarjetas
   WHERE nro_tarjeta = NEW.nro_tarjeta
   FOR UPDATE;

  IF v_perm = 1 THEN
    IF v_saldo - NEW.monto_consumido < -v_lim THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Saldo insuficiente (considerando límite de crédito)';
    END IF;
  ELSE
    IF v_saldo < NEW.monto_consumido THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Saldo insuficiente';
    END IF;
  END IF;

  SET NEW.saldo_anterior = v_saldo;
  SET NEW.saldo_posterior = v_saldo - NEW.monto_consumido;

  UPDATE tarjetas
     SET saldo_actual = NEW.saldo_posterior
   WHERE nro_tarjeta = NEW.nro_tarjeta;
END//

DELIMITER ;

-- =========================================================
-- Vistas operativas del dominio (independientes de Django)
-- =========================================================
CREATE OR REPLACE VIEW v_alertas_pendientes AS
SELECT a.id_alerta AS ID_Alerta,
       a.tipo AS Tipo,
       a.mensaje AS Mensaje,
       a.fecha_creacion AS Fecha_Creacion,
       TIMESTAMPDIFF(HOUR, a.fecha_creacion, NOW()) AS Horas_Pendiente,
       a.estado AS Estado
  FROM alertas_sistema a
 WHERE a.estado = 'Pendiente'
 ORDER BY a.fecha_creacion DESC;

CREATE OR REPLACE VIEW v_recargas_historial AS
SELECT cs.id_carga AS ID_Carga,
       cs.fecha_carga AS Fecha_Carga,
       cs.monto_cargado AS Monto_Cargado,
       cs.nro_tarjeta AS Nro_Tarjeta,
       h.id_hijo AS ID_Hijo,
       CONCAT(h.nombre, ' ', h.apellido) AS Estudiante,
       CONCAT(c.nombres, ' ', c.apellidos) AS Responsable,
       c.telefono AS Telefono,
       t.saldo_actual AS Saldo_Actual_Tarjeta
  FROM cargas_saldo cs
  JOIN tarjetas t ON cs.nro_tarjeta = t.nro_tarjeta
  JOIN hijos h ON t.id_hijo = h.id_hijo
  JOIN clientes c ON h.id_cliente_responsable = c.id_cliente
 WHERE h.activo = 1
 ORDER BY cs.fecha_carga DESC;

CREATE OR REPLACE VIEW v_saldo_tarjetas_compras AS
SELECT t.nro_tarjeta AS Nro_Tarjeta,
       h.nombre AS Estudiante_Nombre,
       h.apellido AS Estudiante_Apellido,
       t.saldo_actual AS Saldo_Actual,
       t.estado AS Estado,
       COALESCE(SUM(ct.monto_consumido),0) AS Total_Consumido,
       COALESCE(SUM(cs.monto_cargado),0) AS Total_Cargado,
       COUNT(DISTINCT ct.id_consumo) AS Cantidad_Compras,
       MAX(ct.fecha_consumo) AS Ultima_Compra
  FROM tarjetas t
  JOIN hijos h ON t.id_hijo = h.id_hijo
  LEFT JOIN consumos_tarjeta ct ON t.nro_tarjeta = ct.nro_tarjeta
  LEFT JOIN cargas_saldo cs ON t.nro_tarjeta = cs.nro_tarjeta
 GROUP BY t.nro_tarjeta, h.nombre, h.apellido, t.saldo_actual, t.estado;

CREATE OR REPLACE VIEW v_stock_alerta AS
SELECT p.id_producto AS ID_Producto,
       p.codigo_barra AS Codigo_Barra,
       p.descripcion AS Descripcion,
       c.nombre AS Categoria,
       s.stock_actual AS Stock_Actual,
       p.stock_minimo AS Stock_Minimo,
       (p.stock_minimo - s.stock_actual) AS Diferencia,
       CASE
         WHEN s.stock_actual = 0 THEN 'CRÍTICO'
         WHEN s.stock_actual <= (p.stock_minimo * 0.5) THEN 'URGENTE'
         ELSE 'ALERTA'
       END AS Nivel_Alerta,
       s.fecha_ultima_actualizacion AS Fecha_Ultima_Actualizacion,
       u.nombre AS Unidad_Medida
  FROM productos p
  JOIN stock_unico s ON p.id_producto = s.id_producto
  JOIN categorias c ON p.id_categoria = c.id_categoria
  LEFT JOIN unidades_medida u ON p.id_unidad_de_medida = u.id_unidad_de_medida
 WHERE p.activo = 1
   AND s.stock_actual <= p.stock_minimo
 ORDER BY s.stock_actual, p.descripcion;

CREATE OR REPLACE VIEW v_ventas_dia AS
SELECT DATE(v.fecha) AS Fecha,
       COUNT(DISTINCT v.id_venta) AS Cantidad_Ventas,
       COALESCE(SUM(v.monto_total),0) AS Total_Vendido,
       COALESCE(SUM(v.saldo_pendiente),0) AS Total_Pendiente,
       COALESCE(SUM(v.monto_total - v.saldo_pendiente),0) AS Total_Pagado,
       COUNT(DISTINCT v.id_cliente) AS Clientes_Atendidos,
       COALESCE(AVG(v.monto_total),0) AS Ticket_Promedio
  FROM ventas v
 WHERE v.fecha >= (CURDATE() - INTERVAL 90 DAY)
 GROUP BY DATE(v.fecha)
 ORDER BY Fecha DESC;

CREATE OR REPLACE VIEW v_saldo_clientes AS
SELECT c.id_cliente AS ID_Cliente,
       c.nombres AS Nombres,
       c.apellidos AS Apellidos,
       CONCAT(c.nombres, ' ', c.apellidos) AS Nombre_Completo,
       c.ruc_ci AS Ruc_CI,
       tc.nombre_tipo AS Tipo_Cliente,
       COALESCE(SUM(CASE WHEN v.estado_pago IN ('PENDIENTE','PARCIAL') THEN v.saldo_pendiente ELSE 0 END),0) AS Saldo_Actual,
       COUNT(v.id_venta) AS Total_Movimientos,
       MAX(v.fecha) AS Ultima_Actualizacion
  FROM clientes c
  LEFT JOIN tipos_cliente tc ON c.id_tipo_cliente = tc.id_tipo_cliente
  LEFT JOIN ventas v ON c.id_cliente = v.id_cliente
 WHERE c.activo = 1
 GROUP BY c.id_cliente;

CREATE OR REPLACE VIEW v_saldo_proveedores AS
SELECT p.id_proveedor AS ID_Proveedor,
       p.razon_social AS Razon_Social,
       p.ruc AS RUC,
       COALESCE(SUM(CASE WHEN c.estado_pago IN ('PENDIENTE','PARCIAL') THEN c.saldo_pendiente ELSE 0 END),0) AS Saldo_Actual,
       COUNT(c.id_compra) AS Total_Compras,
       MAX(c.fecha) AS Ultima_Compra
  FROM proveedores p
  LEFT JOIN compras c ON p.id_proveedor = c.id_proveedor
 WHERE p.activo = 1
 GROUP BY p.id_proveedor;