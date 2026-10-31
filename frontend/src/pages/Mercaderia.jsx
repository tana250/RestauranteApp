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

const horaLocal = () => {
  const ahora = new Date();
  const hh = String(ahora.getHours()).padStart(2, "0");
  const mm = String(ahora.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
};

const crearLinea = () => ({
  key: `${Date.now()}-${Math.random()}`,
  insumoNombre: "",
  insumoId: null,
  cantidad: "",
  unidadMedidaId: "",
  precioUnitario: "",
  tipoInsumoId: "",
  tipoInsumoNombre: "",
  marcaId: "",
  marcaNombre: "",
});

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
  const [lineas, setLineas] = useState([crearLinea()]);
  const [fecha, setFecha] = useState(() => fechaLocal());
  const [hora, setHora] = useState(() => horaLocal());
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

  const handleInsumoNombre = (linea, e) => {
    const nuevoNombre = e.target.value;
    const existente = insumos.find(
      (insumo) => normalizar(insumo.nombre) === normalizar(nuevoNombre)
    );

    setLineas((actuales) =>
      actuales.map((item) =>
        item.key === linea.key
          ? { ...item, insumoNombre: nuevoNombre, insumoId: existente ? existente.id : null }
          : item
      )
    );
  };

  const actualizarLinea = (key, campo, valor) => {
    setLineas((actuales) =>
      actuales.map((linea) => (linea.key === key ? { ...linea, [campo]: valor } : linea))
    );
  };

  const agregarLinea = () => {
    setLineas((actuales) => [...actuales, crearLinea()]);
  };

  const eliminarLinea = (key) => {
    setLineas((actuales) => actuales.filter((linea) => linea.key !== key));
  };

  const handleGuardarIngreso = async (e) => {
    e.preventDefault();
    setMensaje("");
    setError("");

    if (!proveedorNombre.trim()) {
      setError("El proveedor es obligatorio");
      return;
    }

    if (lineas.length === 0) {
      setError("Agregue al menos un insumo");
      return;
    }

    for (const linea of lineas) {
      if (!linea.insumoNombre.trim()) {
        setError("Cada insumo requiere un nombre");
        return;
      }

      const cantidadNumero = Number(linea.cantidad);
      if (!Number.isFinite(cantidadNumero) || cantidadNumero <= 0) {
        setError("Ingrese una cantidad válida");
        return;
      }

      if (!linea.unidadMedidaId) {
        setError("Seleccione una unidad de medida");
        return;
      }

      const precioNumero = Number(linea.precioUnitario);
      if (!Number.isFinite(precioNumero) || precioNumero < 0) {
        setError("Ingrese un precio válido");
        return;
      }
    }

    const ingresos = lineas.map((linea) => ({
      proveedorId: proveedorId || null,
      proveedorNombre: proveedorNombre.trim(),
      insumoId: linea.insumoId || null,
      insumoNombre: linea.insumoNombre.trim(),
      cantidad: Number(linea.cantidad),
      unidadMedidaId: Number(linea.unidadMedidaId),
      precioUnitario: Number(linea.precioUnitario),
      fecha: fecha || fechaLocal(),
      hora: hora || horaLocal(),
      ...(linea.tipoInsumoId ? { tipoInsumoId: Number(linea.tipoInsumoId) } : {}),
      ...(linea.tipoInsumoNombre ? { tipoInsumoNombre: linea.tipoInsumoNombre } : {}),
      ...(linea.marcaId ? { marcaId: Number(linea.marcaId) } : {}),
      ...(linea.marcaNombre ? { marcaNombre: linea.marcaNombre } : {}),
    }));

    setGuardandoIngreso(true);
    try {
      const { data } = await ingresoMercaderiaPanelService.guardar({ ingresos });
      const creado = Array.isArray(data) ? data[0] : data;

      setMensaje(
        `Ingreso registrado: ${creado?.insumoNombre ?? ""} (${creado?.proveedorNombre ?? ""}). ` +
          "Si el insumo es nuevo, completá marca y tipo en el apartado Insumos."
      );
      setLineas([crearLinea()]);

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

          {lineas.map((linea) => (
            <div
              key={linea.key}
              style={{ border: "1px solid #ccc", padding: "0.5rem", marginBottom: "0.5rem" }}
            >
              <p>
                <input
                  list="insumos-existentes-mercaderia"
                  value={linea.insumoNombre}
                  onChange={(e) => handleInsumoNombre(linea, e)}
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
                    value={linea.cantidad}
                    onChange={(e) => actualizarLinea(linea.key, "cantidad", e.target.value)}
                    required
                  />
                </label>{" "}
                <label>
                  Unidad de medida:{" "}
                  <select
                    value={linea.unidadMedidaId}
                    onChange={(e) => actualizarLinea(linea.key, "unidadMedidaId", e.target.value)}
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
                    value={linea.precioUnitario}
                    onChange={(e) => actualizarLinea(linea.key, "precioUnitario", e.target.value)}
                    required
                  />
                </label>
              </p>

              <p>
                <label>
                  Tipo de insumo:{" "}
                  <select
                    value={linea.tipoInsumoId}
                    onChange={(e) => {
                      const valor = e.target.value;
                      if (valor === "__nuevo__") {
                        actualizarLinea(linea.key, "tipoInsumoId", "");
                      } else {
                        actualizarLinea(linea.key, "tipoInsumoId", valor);
                        if (valor) actualizarLinea(linea.key, "tipoInsumoNombre", "");
                      }
                    }}
                  >
                    <option value="">Sin tipo</option>
                    {tiposInsumo.map((tipo) => (
                      <option key={tipo.id} value={String(tipo.id)}>
                        {tipo.tipo}
                      </option>
                    ))}
                    <option value="__nuevo__">Crear nuevo...</option>
                  </select>
                  {linea.tipoInsumoId === "" && (
                    <input
                      value={linea.tipoInsumoNombre}
                      onChange={(e) => actualizarLinea(linea.key, "tipoInsumoNombre", e.target.value)}
                      placeholder="Nombre del nuevo tipo"
                      style={{ marginLeft: "0.5rem" }}
                    />
                  )}
                </label>{" "}
                <label>
                  Marca:{" "}
                  <select
                    value={linea.marcaId}
                    onChange={(e) => {
                      const valor = e.target.value;
                      if (valor === "__nuevo__") {
                        actualizarLinea(linea.key, "marcaId", "");
                      } else {
                        actualizarLinea(linea.key, "marcaId", valor);
                        if (valor) actualizarLinea(linea.key, "marcaNombre", "");
                      }
                    }}
                  >
                    <option value="">Sin marca</option>
                    {marcas.map((marca) => (
                      <option key={marca.id} value={String(marca.id)}>
                        {marca.nombre}
                      </option>
                    ))}
                    <option value="__nuevo__">Crear nuevo...</option>
                  </select>
                  {linea.marcaId === "" && (
                    <input
                      value={linea.marcaNombre}
                      onChange={(e) => actualizarLinea(linea.key, "marcaNombre", e.target.value)}
                      placeholder="Nombre de la nueva marca"
                      style={{ marginLeft: "0.5rem" }}
                    />
                  )}
                </label>
              </p>

              <button
                type="button"
                onClick={() => eliminarLinea(linea.key)}
                disabled={lineas.length === 1}
              >
                Quitar insumo
              </button>
            </div>
          ))}

          <p>
            <button type="button" onClick={agregarLinea}>
              Agregar insumo
            </button>{" "}
            <button type="submit" disabled={guardandoIngreso}>
              {guardandoIngreso ? "Guardando..." : "Registrar ingreso"}
            </button>
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
            </label>{" "}
            <label>
              Hora:{" "}
              <input
                type="time"
                value={hora}
                onChange={(e) => setHora(e.target.value)}
                required
              />
            </label>
          </p>

          <p>
            <small>
              Si el proveedor o el insumo no existen, se creen automáticamente
              al enviar. Los insumos nuevos quedan con la marca y el tipo
              indicados (se crean si no existen).
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
