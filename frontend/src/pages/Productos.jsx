import { useState } from "react";
import ProductoListar from "../components/Producto/ProductoListar";
import useProducto from "../hooks/useProducto";
import useInsumos from "../hooks/useInsumos";
import useUnidadesMedida from "../hooks/useUnidadesMedida";
import * as productoPanelService from "../services/productoPanelService";

const normalizar = (texto) => (texto || "").trim().toLowerCase();

const formatearNumero = (valor) => {
  const numero = Number(valor);
  if (!Number.isFinite(numero)) return "-";
  return numero.toLocaleString("es-AR", { maximumFractionDigits: 3 });
};

const crearFila = (datos = {}) => ({
  key: datos.key ?? `${Date.now()}-${Math.random()}`,
  insumoId: datos.insumoId ?? null,
  nombre: datos.nombre ?? "",
  cantidad: datos.cantidad ?? "",
  unidadMedidaId: datos.unidadMedidaId ?? "",
});

const filasDesdeDetalle = (detalle) => {
  const filas = (detalle.insumos || []).map((item) =>
    crearFila({
      insumoId: item.insumoId,
      nombre: item.insumoNombre || "",
      cantidad: String(item.cantidad ?? ""),
      unidadMedidaId: String(item.unidadMedidaId ?? ""),
    })
  );

  return filas.length > 0 ? filas : [crearFila()];
};

function DetalleProducto({ detalle }) {
  if (!detalle) {
    return <p>Seleccione un producto de la lista para ver su receta y stock.</p>;
  }

  return (
    <div>
      <h3>
        {detalle.nombre} {detalle.activo ? "" : "(inactivo)"}
      </h3>
      <p>Precio: {formatearNumero(detalle.valor)}</p>

      {detalle.insumos.length === 0 ? (
        <p>Este producto no tiene insumos cargados.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Insumo</th>
              <th>Cantidad</th>
              <th>Unidad</th>
              <th>Stock disponible</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {detalle.insumos.map((item) => (
              <tr key={item.id}>
                <td>{item.insumoNombre}</td>
                <td>{formatearNumero(item.cantidad)}</td>
                <td>{item.unidadMedida}</td>
                <td>{formatearNumero(item.stock)}</td>
                <td>{item.suficiente ? "Hay stock" : "Sin stock suficiente"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function Productos() {
  const {
    items: productos,
    loading: cargandoProductos,
    fetchAll: recargarProductos,
    remove: eliminarProducto,
    toggleActivo,
  } = useProducto();
  const { items: insumos } = useInsumos();
  const { items: unidades } = useUnidadesMedida();

  const [vista, setVista] = useState("formulario");
  const [idEditando, setIdEditando] = useState(null);
  const [nombre, setNombre] = useState("");
  const [valor, setValor] = useState("0");
  const [activo, setActivo] = useState(true);
  const [filas, setFilas] = useState(() => [crearFila()]);
  const [detalle, setDetalle] = useState(null);
  const [seleccionadoId, setSeleccionadoId] = useState(null);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  const limpiarFormulario = () => {
    setIdEditando(null);
    setNombre("");
    setValor("0");
    setActivo(true);
    setFilas([crearFila()]);
    setDetalle(null);
    setSeleccionadoId(null);
    setMensaje("");
    setError("");
  };

  const cargarProducto = async (producto, irAFormulario = false) => {
    try {
      setError("");
      const { data } = await productoPanelService.getDetalle(producto.id);
      setIdEditando(data.id);
      setNombre(data.nombre);
      setValor(String(data.valor ?? 0));
      setActivo(Boolean(data.activo));
      setFilas(filasDesdeDetalle(data));
      setDetalle(data);
      setSeleccionadoId(data.id);
      if (irAFormulario) setVista("formulario");
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo cargar el producto");
    }
  };

  const verDetalle = async (producto) => {
    setSeleccionadoId(producto.id);
    try {
      const { data } = await productoPanelService.getDetalle(producto.id);
      setDetalle(data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo cargar el detalle");
    }
  };

  const handleNombreProducto = (e) => {
    const nuevoNombre = e.target.value;
    setNombre(nuevoNombre);
    setMensaje("");

    const existente = productos.find(
      (producto) => normalizar(producto.nombre) === normalizar(nuevoNombre)
    );

    if (existente && existente.id !== idEditando) {
      void cargarProducto(existente);
    }
  };

  const actualizarFila = (key, campo, valorCampo) => {
    setFilas((actuales) =>
      actuales.map((fila) => {
        if (fila.key !== key) return fila;

        if (campo === "nombre") {
          const existente = insumos.find(
            (insumo) => normalizar(insumo.nombre) === normalizar(valorCampo)
          );
          return {
            ...fila,
            nombre: valorCampo,
            insumoId: existente ? existente.id : null,
          };
        }

        return { ...fila, [campo]: valorCampo };
      })
    );
  };

  const agregarFila = () => {
    setFilas((actuales) => [...actuales, crearFila()]);
  };

  const quitarFila = (key) => {
    setFilas((actuales) => actuales.filter((fila) => fila.key !== key));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setError("");

    if (!nombre.trim()) {
      setError("El nombre del producto es obligatorio");
      return;
    }

    const filasConDatos = filas.filter(
      (fila) =>
        fila.nombre.trim() ||
        String(fila.cantidad).trim() ||
        fila.unidadMedidaId
    );

    const insumosPayload = [];

    for (const fila of filasConDatos) {
      if (!fila.nombre.trim()) {
        setError("Complete el nombre de todos los insumos");
        return;
      }

      const cantidad = Number(fila.cantidad);
      if (!Number.isFinite(cantidad) || cantidad <= 0) {
        setError(`Ingrese una cantidad válida para ${fila.nombre}`);
        return;
      }

      if (!fila.unidadMedidaId) {
        setError(`Seleccione una unidad de medida para ${fila.nombre}`);
        return;
      }

      insumosPayload.push({
        insumoId: fila.insumoId || null,
        nombre: fila.nombre.trim(),
        cantidad,
        unidadMedidaId: Number(fila.unidadMedidaId),
      });
    }

    const payload = {
      nombre: nombre.trim(),
      valor: Number(valor || 0),
      activo,
      insumos: insumosPayload,
    };

    if (idEditando) payload.id = idEditando;

    setGuardando(true);
    try {
      const { data } = await productoPanelService.guardar(payload);
      setIdEditando(data.id);
      setNombre(data.nombre);
      setValor(String(data.valor ?? 0));
      setActivo(Boolean(data.activo));
      setFilas(filasDesdeDetalle(data));
      setDetalle(data);
      setSeleccionadoId(data.id);
      setMensaje("Producto guardado correctamente");
      await recargarProductos();
    } catch (err) {
      setError(
        err.response?.data?.error || "No se pudo guardar el producto"
      );
    } finally {
      setGuardando(false);
    }
  };

  const handleEliminar = async (id) => {
    try {
      await eliminarProducto(id);
      if (idEditando === id) limpiarFormulario();
      if (seleccionadoId === id) {
        setDetalle(null);
        setSeleccionadoId(null);
      }
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "No se pudo eliminar el producto (puede tener ventas asociadas)"
      );
    }
  };

  const handleToggleActivo = async (producto) => {
    try {
      await toggleActivo(producto);
      if (idEditando === producto.id) setActivo(!producto.activo);
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo cambiar el estado");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <button
          type="button"
          onClick={() => setVista("formulario")}
          style={{ fontWeight: vista === "formulario" ? "bold" : "normal" }}
        >
          Nuevo / editar producto
        </button>
        <button
          type="button"
          onClick={() => setVista("lista")}
          style={{ fontWeight: vista === "lista" ? "bold" : "normal" }}
        >
          Lista de productos
        </button>
      </div>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {vista === "formulario" ? (
        <form onSubmit={handleSubmit}>
          <h2>{idEditando ? `Editar producto #${idEditando}` : "Nuevo producto"}</h2>

          <p>
            <input
              list="productos-existentes"
              value={nombre}
              onChange={handleNombreProducto}
              placeholder="Nombre del producto"
              required
              style={{ width: "100%", maxWidth: "400px" }}
            />
            <datalist id="productos-existentes">
              {productos.map((producto) => (
                <option key={producto.id} value={producto.nombre} />
              ))}
            </datalist>
          </p>

          <p>
            <label>
              Precio:{" "}
              <input
                type="number"
                min="0"
                step="0.01"
                value={valor}
                onChange={(e) => setValor(e.target.value)}
                required
              />
            </label>
            <label style={{ marginLeft: "1rem" }}>
              <input
                type="checkbox"
                checked={activo}
                onChange={(e) => setActivo(e.target.checked)}
              />{" "}
              Activo
            </label>
          </p>

          <p>
            {idEditando
              ? "Los insumos que figuren acá reemplazan la receta actual."
              : "Cargue los insumos que lleva el producto."}
          </p>

          <table>
            <thead>
              <tr>
                <th>Insumo</th>
                <th>Cantidad</th>
                <th>Unidad de medida</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((fila) => (
                <tr key={fila.key}>
                  <td>
                    <input
                      list="insumos-existentes"
                      value={fila.nombre}
                      onChange={(e) =>
                        actualizarFila(fila.key, "nombre", e.target.value)
                      }
                      placeholder="Nombre del insumo"
                    />
                    {!fila.insumoId && fila.nombre.trim() && (
                      <small> (se creará como insumo nuevo)</small>
                    )}
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0.001"
                      step="0.001"
                      value={fila.cantidad}
                      onChange={(e) =>
                        actualizarFila(fila.key, "cantidad", e.target.value)
                      }
                      style={{ width: "100px" }}
                    />
                  </td>
                  <td>
                    <select
                      value={fila.unidadMedidaId}
                      onChange={(e) =>
                        actualizarFila(
                          fila.key,
                          "unidadMedidaId",
                          e.target.value
                        )
                      }
                    >
                      <option value="">Seleccione...</option>
                      {unidades.map((unidad) => (
                        <option key={unidad.id} value={unidad.id}>
                          {unidad.nombre}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <button
                      type="button"
                      onClick={() => quitarFila(fila.key)}
                    >
                      Quitar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <datalist id="insumos-existentes">
            {insumos.map((insumo) => (
              <option key={insumo.id} value={insumo.nombre} />
            ))}
          </datalist>

          <p>
            <button type="button" onClick={agregarFila}>
              Agregar insumo
            </button>{" "}
            <button type="submit" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar producto"}
            </button>{" "}
            <button type="button" onClick={limpiarFormulario}>
              Nuevo producto
            </button>
          </p>
        </form>
      ) : (
        <section>
          {cargandoProductos && <p>Cargando productos...</p>}
          <ProductoListar
            items={productos}
            selectedId={seleccionadoId}
            onSelect={verDetalle}
            onEdit={(producto) => cargarProducto(producto, true)}
            onRemove={handleEliminar}
            onToggleActivo={handleToggleActivo}
          />

          <h2>Receta y stock</h2>
          <DetalleProducto detalle={detalle} />
        </section>
      )}
    </div>
  );
}
