import { useState } from "react";
import useMesa from "../hooks/useMesa";
import useMozo from "../hooks/useMozo";
import usePersonal from "../hooks/usePersonal";
import useProducto from "../hooks/useProducto";
import * as productoPanelService from "../services/productoPanelService";
import * as ventaPanelService from "../services/ventaPanelService";
import useVenta from "../hooks/useVenta";
import usePagos from "../hooks/usePagos";

const fechaLocal = () => {
  const ahora = new Date();
  const offset = ahora.getTimezoneOffset() * 60000;
  return new Date(ahora.getTime() - offset).toISOString().slice(0, 10);
};

const calcularStockDisponible = (detalle) => {
  if (!detalle) return null;
  const insumosStock = detalle.insumos || [];
  const principal = insumosStock[0];
  if (!principal) return null;
  const cantidad = principal.cantidad > 0 ? principal.cantidad : 0;
  const disponible = cantidad > 0 ? (principal.stock || 0) / cantidad : 0;
  return { ...principal, disponible };
};

export default function Ventas({ onPagar }) {
  const { items: mesas } = useMesa();
  const { items: mozos } = useMozo();
  const { items: personales } = usePersonal();
  const {
    items: productos,
    loading: cargandoProductos,
    fetchAll: recargarProductos,
  } = useProducto();

  const [mesaId, setMesaId] = useState("");
  const [mozoId, setMozoId] = useState("");
  const [fecha, setFecha] = useState(() => fechaLocal());
  const [lineaProducto, setLineaProducto] = useState("");
  const [cantidadProducto, setCantidadProducto] = useState("1");
  const [lineas, setLineas] = useState([]);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [stockProducto, setStockProducto] = useState(null);
  const [cargandoStock, setCargandoStock] = useState(false);
  const [mostrarVentas, setMostrarVentas] = useState(false);

  const { items: ventas, fetchAll: recargarVentas } = useVenta();
  const { items: pagos } = usePagos();

  const mozoSeleccionado = mozos.find((mozo) => mozo.id === Number(mozoId));
  const mozoNombre = mozoSeleccionado
    ? (personales.find((personal) => personal.id === mozoSeleccionado.personalId)?.nombre ??
      null) ?? `Mozo #${mozoSeleccionado.id}`
    : "";

  const stockDisponible = calcularStockDisponible(stockProducto);

  const agregarProducto = () => {
    const producto = productos.find((item) => item.id === Number(lineaProducto));
    const cantidad = Number(cantidadProducto);

    if (!producto) {
      setError("Seleccione un producto");
      return;
    }

    if (!Number.isFinite(cantidad) || cantidad <= 0) {
      setError("La cantidad debe ser mayor a 0");
      return;
    }

    if (stockDisponible && cantidad > stockDisponible.disponible) {
      setError(
        `Stock insuficiente: solo hay ${stockDisponible.disponible} ${stockDisponible.unidadMedida || ""} disponibles para este producto`
      );
      return;
    }

    const lineaExistente = lineas.find(
      (linea) => linea.productoId === producto.id
    );

    if (lineaExistente) {
      setLineas((actuales) =>
        actuales.map((linea) =>
          linea.productoId === producto.id
            ? { ...linea, cantidad, precio: producto.valor }
            : linea
        )
      );
    } else {
      setLineas((actuales) => [
        ...actuales,
        { productoId: producto.id, cantidad, precio: producto.valor },
      ]);
    }

    setLineaProducto("");
    setCantidadProducto("1");
    setError("");
  };

  const quitarLinea = (productoId) => {
    setLineas((actuales) => actuales.filter((linea) => linea.productoId !== productoId));
  };

  const handleProductoSeleccionado = async (id) => {
    const productoId = Number(id);
    if (!productoId) {
      setStockProducto(null);
      return;
    }

    setCargandoStock(true);
    try {
      const { data } = await productoPanelService.getDetalle(productoId);
      setStockProducto(data);
    } catch {
      setStockProducto(null);
    } finally {
      setCargandoStock(false);
    }
  };

  const registrarVenta = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    if (!mesaId) {
      setError("Seleccione una mesa");
      return;
    }

    if (!mozoId) {
      setError("Seleccione un mozo");
      return;
    }

    if (lineas.length === 0) {
      setError("Agregue al menos un producto a la venta");
      return;
    }

    const payload = {
      mesaId: Number(mesaId),
      mozoId: Number(mozoId),
      fecha,
      productos: lineas.map((linea) => ({
        productoId: linea.productoId,
        cantidad: linea.cantidad,
        precio: linea.precio,
      })),
    };

    setGuardando(true);
    try {
      const { data } = await ventaPanelService.guardar(payload);
      setMensaje(`Venta registrada correctamente (id: ${data.id})`);
      setLineas([]);
      await recargarProductos();
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo registrar la venta");
    } finally {
      setGuardando(false);
    }
  };

  const mozoLabel = (id) => {
    const mozo = mozos.find((item) => item.id === id);
    if (!mozo) return `Mozo #${id}`;

    const personal = personales.find(
      (item) => item.id === mozo.personalId
    );
    const nombre = personal?.nombre;

    return nombre ? `${nombre} (Mozo ${mozo.id})` : `Mozo #${mozo.id}`;
  };

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

  return (
    <div>
      <h2>Ventas</h2>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <form onSubmit={registrarVenta}>
        <p>
          <label>
            Mesa:{" "}
            <select value={mesaId} onChange={(e) => setMesaId(e.target.value)} required>
              <option value="">Seleccione...</option>
              {mesas.map((mesa) => (
                <option key={mesa.id} value={mesa.id}>
                  Mesa {mesa.numero}
                </option>
              ))}
            </select>
          </label>{" "}
          <label>
            Mozo:{" "}
            <select value={mozoId} onChange={(e) => setMozoId(e.target.value)} required>
              <option value="">Seleccione...</option>
              {mozos.map((mozo) => (
                <option key={mozo.id} value={mozo.id}>
                  {mozoLabel(mozo.id)}
                </option>
              ))}
            </select>
          </label>{" "}
          <label>
            Fecha:{" "}
            <input
              type="date"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              required
            />
          </label>
        </p>

        <p>
          <label>
            Producto:{" "}
            <select
              value={lineaProducto}
              onChange={(e) => {
                setLineaProducto(e.target.value);
                handleProductoSeleccionado(e.target.value);
              }}
            >
              <option value="">Seleccione...</option>
              {productos.map((producto) => (
                <option key={producto.id} value={producto.id}>
                  {producto.nombre}
                </option>
              ))}
            </select>
          </label>{" "}
          <label>
            Cantidad:{" "}
            <input
              type="number"
              min="0.001"
              step="0.001"
              value={cantidadProducto}
              onChange={(e) => setCantidadProducto(e.target.value)}
            />
          </label>{" "}
          <button type="button" onClick={agregarProducto}>
            Agregar producto
          </button>
        </p>

        {cargandoStock && <p>Cargando stock...</p>}

        {!cargandoStock && stockProducto && stockDisponible && (
          <p>
            Stock disponible:{" "}
            <strong>
              {stockDisponible.disponible} {stockDisponible.unidadMedida || ""}
            </strong>{" "}
            para el producto {stockProducto.nombre}
            {Number(cantidadProducto) > stockDisponible.disponible && (
              <span style={{ color: "crimson" }}>
                {" "}
                (stock insuficiente para la cantidad ingresada)
              </span>
            )}
          </p>
        )}

        {!cargandoStock && stockProducto && !stockDisponible && (
          <p>
            El producto {stockProducto.nombre} no tiene stock disponible.
          </p>
        )}

        {cargandoProductos && <p>Cargando productos...</p>}

        {lineas.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {lineas.map((linea) => {
                const producto = productos.find(
                  (item) => item.id === linea.productoId
                );

                return (
                  <tr key={linea.productoId}>
                    <td>{producto?.nombre ?? `Producto #${linea.productoId}`}</td>
                    <td>{linea.cantidad}</td>
                    <td>{linea.precio}</td>
                    <td>
                      <button
                        type="button"
                        onClick={() => quitarLinea(linea.productoId)}
                      >
                        Quitar
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        <p>
          <button
            type="button"
            onClick={async () => {
              const next = !mostrarVentas;
              setMostrarVentas(next);
              if (next) {
                await recargarVentas();
              }
            }}
          >
            {mostrarVentas ? "Ocultar ventas" : "Ver ventas"}
          </button>
        </p>

        {mostrarVentas && (
          <div>
            <h3>Ventas registradas</h3>
            {ventasPendientes.length === 0 && <p>No hay ventas con pago incompleto.</p>}
            {ventasPendientes.map((venta) => {
              const mesa = mesas.find((item) => item.id === venta.mesaId);
              const mozo = mozos.find((item) => item.id === venta.mozoId);
              const personal = personales.find(
                (item) => item.id === mozo?.personalId
              );
              const productosVenta = venta.productos || [];
              const total = productosVenta.reduce(
                (acc, item) => acc + (item.cantidad || 0) * (item.precio || 0),
                0
              );
              const pagado = (venta.pagos || []).reduce(
                (acc, pago) => acc + (pago.importe || 0),
                0
              );
              const estado =
                pagado >= total ? "Completo" : pagado > 0 ? "Parcial" : "Sin pago";

              return (
                <div
                  key={venta.id}
                  style={{ border: "1px solid #ccc", padding: "0.5rem", marginBottom: "1rem" }}
                >
                  <p>
                    Venta #{venta.id} - {venta.fecha} - Mesa{" "}
                    {mesa?.numero ?? "-"} - Mozo{" "}
                    {personal?.nombre ?? mozo?.id ?? "-"}
                  </p>
                  {productosVenta.length === 0 ? (
                    <p>Sin productos cargados.</p>
                  ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio</th>
                        <th>Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {productosVenta.map((item) => {
                        const producto = productos.find(
                          (prod) => prod.id === item.productoId
                        );

                        return (
                          <tr key={item.id}>
                            <td>{producto?.nombre ?? `Producto #${item.productoId}`}</td>
                            <td>{item.cantidad}</td>
                            <td>{item.precio}</td>
                            <td>{(item.cantidad || 0) * (item.precio || 0)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                  )}
                  <p>
                    <strong>Total: {total}</strong>{" "}
                    <strong>
                      Pagado: {pagado} - Estado: {estado}
                    </strong>
                  </p>
                  {onPagar && (
                    <button type="button" onClick={() => onPagar(venta.id)}>
                      Pagar
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}

        <p>
          <button type="submit" disabled={guardando}>
            {guardando ? "Guardando..." : "Registrar venta"}
          </button>
        </p>
      </form>

      <p>
        <small>
          Mozo seleccionado: {mozoNombre || "Seleccione un mozo"}
        </small>
      </p>
    </div>
  );
}
