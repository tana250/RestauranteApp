import { useEffect, useState } from "react";
import useVenta from "../hooks/useVenta";
import useMetodosPago from "../hooks/useMetodosPago";
import usePagos from "../hooks/usePagos";
import useMesa from "../hooks/useMesa";
import useMozo from "../hooks/useMozo";
import usePersonal from "../hooks/usePersonal";
import useProducto from "../hooks/useProducto";
import { guardar as guardarPago } from "../services/pagosService";

const fechaLocal = () => {
  const ahora = new Date();
  const offset = ahora.getTimezoneOffset() * 60000;
  return new Date(ahora.getTime() - offset).toISOString().slice(0, 10);
};

const horaLocal = () => {
  const ahora = new Date();
  const hh = String(ahora.getHours()).padStart(2, "0");
  const mm = String(ahora.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
};

export default function Pagos({ ventaIdPrevia }) {
  const {
    items: ventas,
    loading: cargandoVentas,
    fetchAll: recargarVentas,
  } = useVenta();
  const { items: metodosPago } = useMetodosPago();
  const { items: pagos, loading: cargandoPagos, fetchAll: recargarPagos } = usePagos();
  const { items: mesas } = useMesa();
  const { items: mozos } = useMozo();
  const { items: personales } = usePersonal();
  const { items: productos } = useProducto();

  const [ventaId, setVentaId] = useState("");
  const [metodoPagoId, setMetodoPagoId] = useState("");
  const [importe, setImporte] = useState("");
  const [fecha, setFecha] = useState(() => fechaLocal());
  const [hora, setHora] = useState(() => horaLocal());
  const [soloCompletos, setSoloCompletos] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (ventaIdPrevia) {
      setVentaId(String(ventaIdPrevia));
      setImporte("");
    }
  }, [ventaIdPrevia]);

  const totalDe = (venta) =>
    (venta.productos || []).reduce(
      (acc, item) => acc + (item.cantidad || 0) * (item.precio || 0),
      0
    );

  const pagadoDe = (venta) =>
    pagos
      .filter((pago) => pago.ventaId === venta.id)
      .reduce((acc, pago) => acc + (pago.importe || 0), 0);

  const ventasPendientes = ventas.filter(
    (venta) => pagadoDe(venta) < totalDe(venta)
  );

  const ventaSeleccionada = ventas.find(
    (venta) => venta.id === Number(ventaId)
  );

  const totalVenta = ventaSeleccionada ? totalDe(ventaSeleccionada) : 0;
  const pagadoVenta = ventaSeleccionada ? pagadoDe(ventaSeleccionada) : 0;

  const nombreMetodo = (id) =>
    metodosPago.find((metodo) => metodo.id === id)?.metodo || `Metodo #${id}`;

  const nombreProducto = (id) =>
    productos.find((producto) => producto.id === id)?.nombre ||
    `Producto #${id}`;

  const infoVenta = (ventaIdBuscado) => {
    const venta = ventas.find((item) => item.id === ventaIdBuscado);
    if (!venta) return null;

    const mesa = mesas.find((item) => item.id === venta.mesaId);
    const mozo = mozos.find((item) => item.id === venta.mozoId);
    const personal = personales.find(
      (item) => item.id === mozo?.personalId
    );

    const productosConNombre = (venta.productos || []).map((item) => ({
      ...item,
      nombre: nombreProducto(item.productoId),
    }));

    const total = productosConNombre.reduce(
      (acc, item) => acc + (item.cantidad || 0) * (item.precio || 0),
      0
    );

    const pagado = pagadoDe(venta);

    return {
      venta,
      mesa: mesa ? `Mesa ${mesa.numero}` : "-",
      mozo: personal?.nombre ?? (mozo ? `Mozo #${mozo.id}` : "-"),
      productos: productosConNombre,
      total,
      pagado,
      estado:
        pagado >= total ? "Completo" : pagado > 0 ? "Parcial" : "Sin pago",
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    if (!ventaId) {
      setError("Seleccione una venta");
      return;
    }

    if (!metodoPagoId) {
      setError("Seleccione un método de pago");
      return;
    }

    const importeNumero = Number(importe);
    if (!Number.isFinite(importeNumero) || importeNumero <= 0) {
      setError("El importe debe ser mayor a 0");
      return;
    }

    try {
      const data = await guardarPago({
        ventaId: Number(ventaId),
        metodoPagoId: Number(metodoPagoId),
        importe: importeNumero,
        fecha,
        hora,
      });
      setMensaje(`Pago registrado correctamente (id: ${data.data.id})`);
      setVentaId("");
      setMetodoPagoId("");
      setImporte("");
      await recargarPagos();
      await recargarVentas();
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo registrar el pago");
    }
  };

  const pagosCompletos = pagos.filter((pago) => {
    const info = infoVenta(pago.ventaId);
    const total = info ? info.total : 0;
    const pagado = info ? info.pagado : 0;
    const completo = pagado >= total;
    return completo;
  });

  const pagosAMostrar = soloCompletos ? pagosCompletos : pagos;

  const importarTotal = () => {
    if (ventaSeleccionada) {
      setImporte(String(totalVenta));
    }
  };

  return (
    <div>
      <h2>Pagos</h2>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <h3>Registrar pago</h3>
      <form onSubmit={handleSubmit}>
        <label>
          Venta (con pago parcial o sin pago):{" "}
          <select
            value={ventaId}
            onChange={(e) => setVentaId(e.target.value)}
            required
          >
            <option value="">Seleccione...</option>
            {cargandoVentas && <option>Cargando ventas...</option>}
            {ventasPendientes.map((venta) => (
              <option key={venta.id} value={venta.id}>
                Venta #{venta.id} - Total: {totalDe(venta)}
              </option>
            ))}
          </select>
        </label>{" "}
        <button
          type="button"
          onClick={importarTotal}
          disabled={!ventaSeleccionada}
        >
          Importar total
        </button>{" "}
        <label>
          Total de la venta: {totalVenta}
        </label>
        <label>
          Método de pago:{" "}
          <select
            value={metodoPagoId}
            onChange={(e) => setMetodoPagoId(e.target.value)}
            required
          >
            <option value="">Seleccione...</option>
            {metodosPago.map((metodo) => (
              <option key={metodo.id} value={metodo.id}>
                {metodo.metodo}
              </option>
            ))}
          </select>
        </label>{" "}
        <label>
          Importe (total o parcial):{" "}
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={importe}
            onChange={(e) => setImporte(e.target.value)}
            placeholder={totalVenta > 0 ? String(totalVenta) : ""}
          />
        </label>{" "}
        <label>
          Fecha:{" "}
          <input
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            required
          />
        </label>{" "}
        <label>
          Hora:{" "}
          <input
            type="time"
            value={hora}
            onChange={(e) => setHora(e.target.value)}
            required
          />
        </label>{" "}
        <button type="submit">Registrar pago</button>
      </form>

      <p>
        <strong>Pagado actual:</strong> {pagadoVenta} / Total: {totalVenta}
      </p>

      <h3>Pagos registrados</h3>
      <label>
        <input
          type="checkbox"
          checked={soloCompletos}
          onChange={(e) => setSoloCompletos(e.target.checked)}
        />{" "}
        Solo mostrar pagos completos
      </label>
      {cargandoPagos && <p>Cargando pagos...</p>}
      {!cargandoPagos && (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Venta</th>
              <th>Método</th>
              <th>Importe</th>
              <th>Fecha</th>
              <th>Mesa</th>
              <th>Mozo</th>
              <th>Productos</th>
              <th>Total venta</th>
              <th>Pagado</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {pagosAMostrar.map((pago) => {
              const info = infoVenta(pago.ventaId);
              const total = info ? info.total : 0;
              const pagado = info ? info.pagado : 0;

              return (
                <tr key={pago.id}>
                  <td>{pago.id}</td>
                  <td>{pago.ventaId}</td>
                  <td>{nombreMetodo(pago.metodoPagoId)}</td>
                  <td>{pago.importe}</td>
                  <td>{pago.fecha}</td>
                  <td>{pago.hora}</td>
                  <td>{info ? info.mesa : "-"}</td>
                  <td>{info ? info.mozo : "-"}</td>
                  <td>
                    {info
                      ? info.productos
                          .map(
                            (item) =>
                              `${item.nombre} x${item.cantidad} (total: ${
                                (item.cantidad || 0) * (item.precio || 0)
                              })`
                          )
                          .join(", ")
                      : "-"}
                  </td>
                  <td>{total}</td>
                  <td>{pagado}</td>
                  <td>{info ? info.estado : "Sin pago"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
