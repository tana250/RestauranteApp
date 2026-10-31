import useIngresoMercaderia from "../hooks/useIngresoMercaderia";
import useEgresoMercaderia from "../hooks/useEgresoMercaderia";

export default function Stock() {
  const { items: ingresos, loading: cargandoIngresos } = useIngresoMercaderia();
  const { items: egresos, loading: cargandoEgresos } = useEgresoMercaderia();

  const egresosPorIngreso = {};
  egresos.forEach((egreso) => {
    const key = egreso.ingresoMercaderiaId;
    egresosPorIngreso[key] = (egresosPorIngreso[key] || 0) + (egreso.cantidad || 0);
  });

  const filas = ingresos.map((ingreso) => {
    const egresado = egresosPorIngreso[ingreso.id] || 0;
    const stock = (ingreso.cantidad || 0) - egresado;

    return { ...ingreso, egresado, stock };
  });

  return (
    <div>
      <h2>Stock</h2>
      <p>Stock actual = ingresos - egresos.</p>

      {cargandoIngresos && <p>Cargando ingresos...</p>}
      {cargandoEgresos && <p>Cargando egresos...</p>}

      {!cargandoIngresos && !cargandoEgresos && (
        <table>
          <thead>
            <tr>
              <th>Ingreso</th>
              <th>Insumo</th>
              <th>Proveedor</th>
              <th>Unidad</th>
              <th>Cantidad ingresada</th>
              <th>Precio unitario</th>
              <th>Fecha</th>
              <th>Hora</th>
              <th>Egresado</th>
              <th>Stock actual</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila) => (
              <tr key={fila.id}>
                <td>{fila.id}</td>
                <td>{fila.insumoNombre}</td>
                <td>{fila.proveedorNombre}</td>
                <td>{fila.unidadMedida}</td>
                <td>{fila.cantidad}</td>
                <td>{fila.precioUnitario}</td>
                <td>{fila.fecha}</td>
                <td>{fila.hora}</td>
                <td>{fila.egresado}</td>
                <td>{fila.stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
