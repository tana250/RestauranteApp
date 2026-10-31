# Esquema de Base de Datos - RestauranteApp

## unidadesMedida


| Campo  | Tipo de Dato | Restricciones            | Descripción                                        |
| ------ | ------------ | ------------------------ | --------------------------------------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único                                |
| nombre | String(50)   | NOT NULL, UNIQUE         | Nombre de la unidad de medida (kg, g, lt, ml, etc.) |

**Tabla:** `unidades_medida`

---

## proveedor


| Campo  | Tipo de Dato | Restricciones            | Descripción         |
| ------ | ------------ | ------------------------ | -------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100)  | NOT NULL, UNIQUE         | Nombre del proveedor |

**Tabla:** `proveedor`

---

## tiposInsumo


| Campo | Tipo de Dato | Restricciones            | Descripción         |
| ----- | ------------ | ------------------------ | -------------------- |
| id    | Integer      | PK, AutoIncrement, Index | Identificador único |
| tipo  | String(50)   | NOT NULL, UNIQUE         | Tipo de insumo       |

**Tabla:** `tipos_insumo`

---

## marcas


| Campo  | Tipo de Dato | Restricciones            | Descripción         |
| ------ | ------------ | ------------------------ | -------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único |
| nombre | String(100)  | NOT NULL, UNIQUE         | Nombre de la marca   |

**Tabla:** `marcas`

---

## insumos


| Campo        | Tipo de Dato | Restricciones                    | Descripción                 |
| ------------ | ------------ | -------------------------------- | ---------------------------- |
| id           | Integer      | PK, AutoIncrement, Index    | Identificador único         |
| nombre       | String(100)  | NOT NULL                    | Nombre del insumo            |
| tipoInsumoId | Integer      | FK -> tipos_insumo(id), NULL | Referencia al tipo de insumo |
| marcaId      | Integer      | FK -> marcas(id), NULL      | Referencia a la marca        |

**Tabla:** `insumos`

**Relaciones:**

- `tipoInsumoId` → `tipos_insumo(id)`
- `marcaId` → `marcas(id)`

> `tipoInsumoId` y `marcaId` pueden ser NULL. El panel de productos crea
> insumos nuevos sólo con el nombre; esos datos se completan después desde
> el panel de insumos.

**Clave única:** `(marcaId, nombre)` — clave compuesta sobre la que se
identifica un insumo (nombre de producto de una misma marca). No se
repite un mismo insumo para la misma marca.

---

## ingresoMercaderia


| Campo          | Tipo de Dato   | Restricciones                       | Descripción                                      |
| -------------- | -------------- | ----------------------------------- | ------------------------------------------------- |
| id             | Integer        | PK, AutoIncrement, Index            | Identificador único                              |
| proveedorId    | Integer        | FK -> proveedor(id), NOT NULL       | Referencia al proveedor                           |
| insumoId       | Integer        | FK -> insumos(id), NOT NULL         | Referencia al insumo                              |
| unidadMedidaId | Integer        | FK -> unidades_medida(id)           | Referencia a la unidad de medida                  |
| cantidad       | Numeric(10, 3) | NOT NULL                            | Cantidad ingresada                                |
| precioUnitario | Numeric(10, 2) | NOT NULL                            | Precio unitario del insumo al momento del ingreso |
| fecha          | DateTime      | NOT NULL                            | Fecha de ingreso de la mercadería                |
| hora           | Time          | NOT NULL                            | Hora de ingreso de la mercadería                |

**Tabla:** `ingreso_mercaderia`

**Relaciones:**

- `proveedorId` → `proveedor(id)`
- `insumoId` → `insumos(id)`
- `unidadMedidaId` → `unidades_medida(id)`

---

## recetasProductos


| Campo          | Tipo de Dato   | Restricciones                       | Descripción                                |
| -------------- | -------------- | ----------------------------------- | ------------------------------------------- |
| id             | Integer        | PK, AutoIncrement, Index            | Identificador único                        |
| productoId     | Integer        | FK -> producto(id), NOT NULL        | Referencia al producto                      |
| insumoId       | Integer        | FK -> insumos(id), NOT NULL         | Referencia al insumo                        |
| cantidad       | Numeric(10, 3) | NOT NULL                            | Cantidad de insumo requerida para la receta |
| unidadMedidaId | Integer        | FK -> unidades_medida(id), NOT NULL | Referencia a la unidad de medida            |

**Tabla:** `recetas_productos`

**Restricciones:** `UNIQUE (productoId, insumoId)` — un producto no puede
listar el mismo insumo más de una vez en su receta.

**Relaciones:**

- `productoId` → `producto(id)`
- `insumoId` → `insumos(id)`
- `unidadMedidaId` → `unidades_medida(id)`

---

## producto


| Campo  | Tipo de Dato   | Restricciones            | Descripción                       |
| ------ | -------------- | ------------------------ | ---------------------------------- |
| id     | Integer        | PK, AutoIncrement, Index | Identificador único               |
| nombre | String(100)    | NOT NULL                 | Nombre del producto                |
| valor  | Numeric(10, 2) | NOT NULL                 | Precio de venta del producto       |
| activo | Boolean        | NOT NULL, DEFAULT TRUE   | Indica si el producto está activo |

**Tabla:** `producto`

---

## personal


| Campo  | Tipo de Dato | Restricciones            | Descripción         |
| :----- | ------------ | ------------------------ | :------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único |
| dni    | String(20)   | NOT NULL, UNIQUE         | DNI del personal     |
| nombre | String(100)  | NOT NULL                 | Nombre del personal  |
| activo | Boolean      | DEFAULT 1 | Indica si el Personal esta activo |

**Tabla:** `personal`

---

## mozo


| Campo      | Tipo de Dato | Restricciones                        | Descripción           |
| ---------- | ------------ | ------------------------------------ | ---------------------- |
| id         | Integer      | PK, AutoIncrement, Index             | Identificador único   |
| personalId | Integer      | FK -> personal(id), NOT NULL, UNIQUE | Referencia al personal |

**Tabla:** `mozo`

**Relaciones:**

- `personalId` → `personal(id)`

---

## mesa


| Campo  | Tipo de Dato | Restricciones            | Descripción         |
| ------ | ------------ | ------------------------ | -------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único |
| numero | Integer      | NOT NULL, UNIQUE         | Número de mesa      |

**Tabla:** `mesa`

---

## egresoMercaderia


| Campo               | Tipo de Dato   | Restricciones                          | Descripción                         |
| ------------------- | -------------- | -------------------------------------- | ------------------------------------ |
| id                  | Integer        | PK, AutoIncrement, Index               | Identificador único                 |
| ventaId             | Integer        | FK -> venta(id), NULL                 | Venta de la que se egresó; NULL si es consumo de personal |
| ingresoMercaderiaId | Integer        | FK -> ingreso_mercaderia(id), NOT NULL | Referencia al ingreso de mercadería |
| cantidad            | Numeric(10, 3) | NOT NULL                               | Cantidad egresada                    |

**Tabla:** `egreso_mercaderia`

**Relaciones:**

- `ingresoMercaderiaId` → `ingreso_mercaderia(id)`

---

## venta


| Campo  | Tipo de Dato | Restricciones            | Descripción         |
| ------ | ------------ | ------------------------ | -------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único |
| mozoId | Integer      | FK -> mozo(id), NOT NULL | Referencia al mozo   |
| mesaId | Integer      | FK -> mesa(id), NOT NULL | Referencia a la mesa |
| fecha  | DateTime     | NOT NULL                 | Fecha de la venta    |
| hora   | Time         | NOT NULL                 | Hora de la venta    |


**Tabla:** `venta`

**Relaciones:**

- `mozoId` → `mozo(id)`
- `mesaId` → `mesa(id)`

---

## productoVenta


| Campo              | Tipo de Dato   | Restricciones                         | Descripción                               |
| ------------------ | -------------- | ------------------------------------- | ------------------------------------------ |
| id                 | Integer        | PK, AutoIncrement, Index              | Identificador único                       |
| ventaId            | Integer        | FK -> venta(id), NOT NULL             | Referencia a la venta                      |
| productoId         | Integer        | FK -> producto(id), NOT NULL          | Referencia al producto                     |
| precio             | Numeric(10, 2) | NOT NULL                              | Precio del producto al momento de la venta |
| cantidad | integer | not null | cantidad de producto vendido |


**Tabla:** `producto_venta`

**Relaciones:**

- `ventaId` → `venta(id)`
- `productoId` → `producto(id)`

---

## consumoPersonal


| Campo              | Tipo de Dato | Restricciones                         | Descripción                        |
| ------------------ | ------------ | ------------------------------------- | ----------------------------------- |
| id                 | Integer      | PK, AutoIncrement, Index              | Identificador único                |
| personalId         | Integer      | FK -> personal(id), NOT NULL          | Referencia al personal              |
| egresoMercaderiaId | Integer      | FK -> egreso_mercaderia(id), NOT NULL | Referencia al egreso de mercadería |
| fecha              | DateTime     | NOT NULL                              | Fecha del consumo |
| hora               | Time         | NOT NULL                              | Hora del consumo |


**Tabla:** `consumo_personal`

**Relaciones:**

- `personalId` → `personal(id)`
- `egresoMercaderiaId` → `egreso_mercaderia(id)`

---

## metodosPago


| Campo  | Tipo de Dato | Restricciones            | Descripción               |
| ------ | ------------ | ------------------------ | -------------------------- |
| id     | Integer      | PK, AutoIncrement, Index | Identificador único       |
| metodo | String(50)   | NOT NULL, UNIQUE         | Nombre del método de pago |

**Tabla:** `metodos_pago`

---

## pagos


| Campo        | Tipo de Dato   | Restricciones                   | Descripción                  |
| ------------ | -------------- | ------------------------------- | ----------------------------- |
| id           | Integer        | PK, AutoIncrement, Index        | Identificador único          |
| ventaId      | Integer        | FK -> venta(id), NOT NULL       | Referencia a la venta         |
| metodoPagoId | Integer        | FK -> metodosPago(id), NOT NULL | Referencia al método de pago |
| importe      | Numeric(10, 2) | NOT NULL                        | Importe pagado                |
| fecha        | Date           | NOT NULL                        | Fecha del pago                |
| hora         | Time           | NOT NULL                        | Hora del pago                |


**Tabla:** `pagos`

**Relaciones:**

- `ventaId` → `venta(id)`
- `metodoPagoId` → `metodosPago(id)`