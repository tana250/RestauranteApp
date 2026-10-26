# Resumen de cambios

- Agregadas entidades: personal, mozo, mesa, egresoMercaderia, venta, productoVenta, consumoPersonal, metodosPago, pagos
- Personal: id, dni, nombre
- Mozo: id, personalId (FK personal.id)
- Mesa: id, numero
- EgresoMercaderia: id, ingresoMercaderiaId (FK ingreso_mercaderia.id), cantidad
- Venta: id, mozoId (FK mozo.id), mesaId (FK mesa.id), fecha
- ProductoVenta: id, ventaId (FK venta.id), productoId (FK producto.id), precio, egresoMercaderiaId (FK egreso_mercaderia.id)
- ConsumoPersonal: id, personalId (FK personal.id), egresoMercaderiaId (FK egreso_mercaderia.id), fecha
- MetodosPago: id, metodo
- Pagos: id, ventaId (FK venta.id), metodoPagoId (FK metodosPago.id), importe, fecha
- Modelos creados con estilo Mapped/mapped_column + relaciones + to_json/from_json/update_from_json
- CRUDs creados con register_api (ItemAPI/GroupAPI)
- api/__init__.py actualizado para registrar todas las nuevas APIs
