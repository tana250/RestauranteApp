# Esquema de Base de Datos - RestauranteApp

## unidadesMedida
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| nombre | String(50) | NOT NULL, UNIQUE | Nombre de la unidad de medida (kg, g, lt, ml, etc.) |

**Tabla:** `unidades_medida`

---

## proveedor
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100) | NOT NULL, UNIQUE | Nombre del proveedor |

**Tabla:** `proveedor`

---

## tiposInsumo
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| tipo | String(50) | NOT NULL, UNIQUE | Tipo de insumo |

**Tabla:** `tipos_insumo`

---

## marcas
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100) | NOT NULL, UNIQUE | Nombre de la marca |

**Tabla:** `marcas`

---

## insumos
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100) | NOT NULL | Nombre del insumo |
| tipoInsumoId | Integer | FK -> tipos_insumo(id), NOT NULL | Referencia al tipo de insumo |
| marcaId | Integer | FK -> marcas(id), NOT NULL | Referencia a la marca |

**Tabla:** `insumos`

**Relaciones:**
- `tipoInsumoId` → `tipos_insumo(id)`
- `marcaId` → `marcas(id)`

---

## ingresoMercaderia
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| proveedorId | Integer | FK -> proveedor(id), NOT NULL | Referencia al proveedor |
| insumoId | Integer | FK -> insumos(id), NOT NULL | Referencia al insumo |
| unidadMedidaId | Integer | FK -> unidades_medida(id), NOT NULL | Referencia a la unidad de medida |
| cantidad | Numeric(10, 3) | NOT NULL | Cantidad ingresada |
| precioUnitario | Numeric(10, 2) | NOT NULL | Precio unitario del insumo al momento del ingreso |
| fecha | Date | NOT NULL | Fecha de ingreso de la mercadería |

**Tabla:** `ingreso_mercaderia`

**Relaciones:**
- `proveedorId` → `proveedor(id)`
- `insumoId` → `insumos(id)`
- `unidadMedidaId` → `unidades_medida(id)`

---

## recetasProductos
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| productoId | Integer | FK -> producto(id), NOT NULL | Referencia al producto |
| insumoId | Integer | FK -> insumos(id), NOT NULL | Referencia al insumo |
| cantidad | Numeric(10, 3) | NOT NULL | Cantidad de insumo requerida para la receta |
| unidadMedidaId | Integer | FK -> unidades_medida(id), NOT NULL | Referencia a la unidad de medida |

**Tabla:** `recetas_productos`

**Relaciones:**
- `productoId` → `producto(id)`
- `insumoId` → `insumos(id)`
- `unidadMedidaId` → `unidades_medida(id)`

---

## producto
| Campo | Tipo de Dato | Restricciones | Descripción |
|---|---|---|---|
| id | Integer | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100) | NOT NULL | Nombre del producto |
| valor | Numeric(10, 2) | NOT NULL | Precio de venta del producto |
| activo | Boolean | NOT NULL, DEFAULT TRUE | Indica si el producto está activo |

**Tabla:** `producto`

---
## personal
1.id
2.dni
3.nombre


## mozo
1.id
2.personalId

## mesa
1.id
2.numero


## productoVenta
1.id
2.ventaId
3.productoId
4.precio
5.egresoMercaderiaId


## venta
1.mozoId
2.mesaId
3.fecha

## consumoPersonal
1.id
2.personalId
3.egresoMercaderiaId
3.fecha


## egresoMercaderia
1.id
2.ingresoMercaderiaId
3.cantidad

## metodosPago
1.id
2.metodo

## pagos
1.id
2.ventaId
3.metodoPagoId
4.importe
5.fecha


