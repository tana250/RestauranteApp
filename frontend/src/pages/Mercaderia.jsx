import { useState } from "react";
import useProveedor from "../hooks/useProveedor";
import useInsumos from "../hooks/useInsumos";
import useUnidadesMedida from "../hooks/useUnidadesMedida";
import useMarcas from "../hooks/useMarcas";
import useTiposInsumo from "../hooks/useTiposInsumo";
import * as ingresoMercaderiaPanelService from "../services/ingresoMercaderiaPanelService";
import * as insumosPanelService from "../services/insumosPanelService";

const normalizar = (texto) => (texto || "").trim().toLowerCase();

const fechaLocal = () => {
  const ahora = new Date();
  const offset = ahora.getTimezoneOffset() * 60000;
  return new Date(ahora.getTime() - offset).toISOString().slice(0, 10);
};

export default function Mercaderia() {
  const {
    items: proveedores,
    fetchAll: recargarProveedores,
  } = useProveedor();
  const { items: insumos, fetchAll: recargarInsumos } = useInsumos();
  const { items: unidades } = useUnidadesMedida();
  const { items: marcas } = useMarcas();
  const { items: tiposInsumo } = useTiposInsumo();

  const [vista, setVista] = useState("ingresos");
  const [proveedorNombre, setProveedorNombre] = useState("");
  const [proveedorId, setProveedorId] = useState(null);
  const [insumoNombre, setInsumoNombre] = useState("");
  const [insumoId, setInsumoId] = useState(null);
  const [cantidad, setCantidad] = useState("");
  const [unidadMedidaId, setUnidadMedidaId] = useState("");
  const [precioUnitario, setPrecioUnitario] = useState("");
  const [fecha, setFecha] = useState(() => fechaLocal());
  const [guardandoIngreso, setGuardandoIngreso] = useState(false);

  const [cambios, setCambios] = useState({});
  const [guardandoInsumos, setGuardandoInsumos] = useState(false);

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const hayCambiosInsumos = Object.keys(cambios).length > 0;

  const handleProveedorNombre = (e) => {
    const nuevoNombre = e.target.value;
    setProveedorNombre(nuevoNombre);
    setMensaje("");

    const existente = proveedores.find(
      (proveedor) => normalizar(proveedor.nombre) === normalizar(nuevoNombre)
    );
    setProveedorId(existente ? existente.id : null);
  };

  const handleInsumoNombre = (e) => {
    const nuevoNombre = e.target.value;
    setInsumoNombre(nuevoNombre);
    setMensaje("");

    const existente = insumos.find(
      (insumo) => normalizar(insumo.nombre) === normalizar(nuevoNombre)
    );
    setInsumoId(existente ? existente.id : null);
  };

  const handleGuardarIngreso = async (e) => {
    e.preventDefault();
    setMensaje("");
    setError("");

    if (!proveedorNombre.trim()) {
      setError("El proveedor es obligatorio");
      return;
    }

    if (!insumoNombre.trim()) {
      setError("El insumo es obligatorio");
      return;
    }

    const cantidadNumero = Number(cantidad);
    if (!Number.isFinite(cantidadNumero) || cantidadNumero <= 0) {
      setError("Ingrese una cantidad válida");
      return;
    }

    if (!unidadMedidaId) {
      setError("Seleccione una unidad de medida");
      return;
    }

    const precioNumero = Number(precioUnitario);
    if (!Number.isFinite(precioNumero) || precioNumero < 0) {
      setError("Ingrese un precio válido");
      return;
    }

    const payload = {
      proveedorId: proveedorId || null,
      proveedorNombre: proveedorNombre.trim(),
      insumoId: insumoId || null,
      insumoNombre: insumoNombre.trim(),
      cantidad: cantidadNumero,
      unidadMedidaId: Number(unidadMedidaId),
      precioUnitario: precioNumero,
      fecha: fecha || fechaLocal(),
    };

    setGuardandoIngreso(true);
    try {
      const { data } = await ingresoMercaderiaPanelService.guardar(payload);
      setProveedorId(data.proveedorId ?? null);
      setMensaje(
        `Ingreso registrado: ${data.insumoNombre} (${data.proveedorNombre}). ` +
          "Si el insumo es nuevo, completá marca y tipo en el apartado Insumos."
      );
      setInsumoNombre("");
      setInsumoId(null);
      setCantidad("");
      setPrecioUnitario("");

      await Promise.all([recargarInsumos(), recargarProveedores()]);
    } catch (err) {
      setError(
        err.response?.data?.error || "No se pudo registrar el ingreso"
      );
    } finally {
      setGuardandoIngreso(false);
    }
  };

  const valorSelect = (insumo, campo) => {
    const cambio = cambios[insumo.id];

    if (cambio && cambio[campo] !== undefined) {
      return cambio[campo];
    }

    return insumo[campo] == null ? "" : String(insumo[campo]);
  };

  const handleCambioInsumo = (id, campo, valor) => {
    setCambios((actuales) => ({
      ...actuales,
      [id]: {
        ...(actuales[id] || {}),
        [campo]: valor,
      },
    }));
    setMensaje("");
  };

  const handleGuardarInsumos = async () => {
    setMensaje("");
    setError("");

    const payload = insumos
      .filter((insumo) => cambios[insumo.id])
      .map((insumo) => {
        const marcaId = valorSelect(insumo, "marcaId");
        const tipoInsumoId = valorSelect(insumo, "tipoInsumoId");

        return {
          id: insumo.id,
          marcaId: marcaId === "" ? null : Number(marcaId),
          tipoInsumoId:
            tipoInsumoId === "" ? null : Number(tipoInsumoId),
        };
      });

    if (payload.length === 0) {
      setCambios({});
      return;
    }

    setGuardandoInsumos(true);
    try {
      await insumosPanelService.guardar({ insumos: payload });
      setCambios({});
      setMensaje("Insumos actualizados correctamente");
      await recargarInsumos();
    } catch (err) {
      setError(
        err.response?.data?.error || "No se pudieron guardar los insumos"
      );
    } finally {
      setGuardandoInsumos(false);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <button
          type="button"
          onClick={() => setVista("ingresos")}
          style={{ fontWeight: vista === "ingresos" ? "bold" : "normal" }}
        >
          Ingresos
        </button>
        <button
          type="button"
          onClick={() => setVista("insumos")}
          style={{ fontWeight: vista === "insumos" ? "bold" : "normal" }}
        >
          Insumos
        </button>
      </div>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {vista === "ingresos" ? (
        <form onSubmit={handleGuardarIngreso}>
          <h2>Nuevo ingreso de mercadería</h2>

          <p>
            <input
              list="proveedores-existentes"
              value={proveedorNombre}
              onChange={handleProveedorNombre}
              placeholder="Proveedor"
              required
              style={{ width: "100%", maxWidth: "400px" }}
            />
            <datalist id="proveedores-existentes">
              {proveedores.map((proveedor) => (
                <option key={proveedor.id} value={proveedor.nombre} />
              ))}
            </datalist>
          </p>

          <p>
            <input
              list="insumos-existentes-mercaderia"
              value={insumoNombre}
              onChange={handleInsumoNombre}
              placeholder="Insumo"
              required
              style={{ width: "100%", maxWidth: "400px" }}
            />
            <datalist id="insumos-existentes-mercaderia">
              {insumos.map((insumo) => (
                <option key={insumo.id} value={insumo.nombre} />
              ))}
            </datalist>
          </p>

          <p>
            <label>
              Cantidad:{" "}
              <input
                type="number"
                min="0.001"
                step="0.001"
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                required
              />
            </label>{" "}
            <label>
              Unidad de medida:{" "}
              <select
                value={unidadMedidaId}
                onChange={(e) => setUnidadMedidaId(e.target.value)}
                required
              >
                <option value="">Seleccione...</option>
                {unidades.map((unidad) => (
                  <option key={unidad.id} value={unidad.id}>
                    {unidad.nombre}
                  </option>
                ))}
              </select>
            </label>{" "}
            <label>
              Precio unitario:{" "}
              <input
                type="number"
                min="0"
                step="0.01"
                value={precioUnitario}
                onChange={(e) => setPrecioUnitario(e.target.value)}
                required
              />
            </label>
          </p>

          <p>
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
            <button type="submit" disabled={guardandoIngreso}>
              {guardandoIngreso ? "Guardando..." : "Registrar ingreso"}
            </button>
          </p>

          <p>
            <small>
              Si el proveedor o el insumo no existen, se crean automáticamente
              al enviar. Los insumos nuevos quedan sin marca ni tipo hasta que
              los completes en el apartado Insumos.
            </small>
          </p>
        </form>
      ) : (
        <section>
          <h2>Insumos</h2>
          <p>
            Asigná marca y tipo de insumo. Todos los cambios se envían en un
            solo JSON y se guardan en una sola transacción.
          </p>

          {insumos.length === 0 ? (
            <p>No hay insumos cargados. Registrá un ingreso para crearlos.</p>
          ) : (
            <>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Insumo</th>
                    <th>Marca</th>
                    <th>Tipo de insumo</th>
                  </tr>
                </thead>
                <tbody>
                  {insumos.map((insumo) => (
                    <tr key={insumo.id}>
                      <td>{insumo.id}</td>
                      <td>{insumo.nombre}</td>
                      <td>
                        <select
                          value={valorSelect(insumo, "marcaId")}
                          onChange={(e) =>
                            handleCambioInsumo(
                              insumo.id,
                              "marcaId",
                              e.target.value
                            )
                          }
                        >
                          <option value="">Sin marca</option>
                          {marcas.map((marca) => (
                            <option key={marca.id} value={marca.id}>
                              {marca.nombre}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <select
                          value={valorSelect(insumo, "tipoInsumoId")}
                          onChange={(e) =>
                            handleCambioInsumo(
                              insumo.id,
                              "tipoInsumoId",
                              e.target.value
                            )
                          }
                        >
                          <option value="">Sin tipo</option>
                          {tiposInsumo.map((tipo) => (
                            <option key={tipo.id} value={tipo.id}>
                              {tipo.tipo}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <p>
                <button
                  type="button"
                  onClick={handleGuardarInsumos}
                  disabled={!hayCambiosInsumos || guardandoInsumos}
                >
                  {guardandoInsumos ? "Guardando..." : "Guardar cambios"}
                </button>{" "}
                <button
                  type="button"
                  onClick={() => setCambios({})}
                  disabled={!hayCambiosInsumos || guardandoInsumos}
                >
                  Descartar cambios
                </button>{" "}
                <small>
                  {hayCambiosInsumos
                    ? `${Object.keys(cambios).length} insumo(s) con cambios`
                    : "Sin cambios pendientes"}
                </small>
              </p>
            </>
          )}
        </section>
      )}
    </div>
  );
}
