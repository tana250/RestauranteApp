import { useState } from "react";
import usePersonal from "../hooks/usePersonal";
import useInsumos from "../hooks/useInsumos";
import useUnidadesMedida from "../hooks/useUnidadesMedida";
import * as consumoPersonalService from "../services/consumoPersonalService";

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
  insumoId: null,
  insumoNombre: "",
  cantidad: "",
  unidadMedidaId: "",
});

export default function ConsumoPersonal() {
  const { items: personales, loading: cargandoPersonales } = usePersonal();
  const { items: insumos } = useInsumos();
  const { items: unidades, loading: cargandoUnidades } = useUnidadesMedida();

  const [personalId, setPersonalId] = useState("");
  const [fecha, setFecha] = useState(() => fechaLocal());
  const [hora, setHora] = useState(() => horaLocal());
  const [lineas, setLineas] = useState([crearLinea()]);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    if (!personalId) {
      setError("Seleccione un personal");
      return;
    }

    if (!fecha) {
      setError("La fecha es obligatoria");
      return;
    }

    if (!hora) {
      setError("La hora es obligatoria");
      return;
    }

    if (lineas.length === 0) {
      setError("Agregue al menos un insumo");
      return;
    }

    for (const linea of lineas) {
      if (!linea.insumoNombre.trim()) {
        setError("Cada consumo requiere un insumo");
        return;
      }

      const cantidad = Number(linea.cantidad);
      if (!Number.isFinite(cantidad) || cantidad <= 0) {
        setError("Ingrese una cantidad válida");
        return;
      }

      if (!linea.unidadMedidaId) {
        setError("Seleccione una unidad de medida");
        return;
      }
    }

    const data = {
      personalId: Number(personalId),
      fecha,
      hora,
      egresos: lineas.map((linea) => ({
        insumoId: linea.insumoId || null,
        insumoNombre: linea.insumoNombre.trim(),
        cantidad: Number(linea.cantidad),
        unidadMedidaId: Number(linea.unidadMedidaId),
      })),
    };

    setGuardando(true);
    try {
      const { data: respuesta } = await consumoPersonalService.guardar(data);
      setMensaje(
        `Consumo registrado correctamente (id: ${respuesta?.[0]?.id ?? respuesta?.id ?? ""}).`
      );
      setLineas([crearLinea()]);
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo registrar el consumo");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div>
      <h2>Consumo personal</h2>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Personal:{" "}
            <select value={personalId} onChange={(e) => setPersonalId(e.target.value)} required>
              <option value="">Seleccione...</option>
              {cargandoPersonales && <option>Cargando personal...</option>}
              {personales.map((personal) => (
                <option key={personal.id} value={personal.id}>
                  {personal.nombre}
                </option>
              ))}
            </select>
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

        <h3>Insumos consumidos</h3>
        {lineas.map((linea) => (
          <div
            key={linea.key}
            style={{ border: "1px solid #ccc", padding: "0.5rem", marginBottom: "0.5rem" }}
          >
            <p>
              <input
                list="insumos-existentes-consumo"
                value={linea.insumoNombre}
                onChange={(e) => handleInsumoNombre(linea, e)}
                placeholder="Insumo"
                required
              />
              <datalist id="insumos-existentes-consumo">
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
                  {cargandoUnidades && <option>Cargando unidades...</option>}
                  {unidades.map((unidad) => (
                    <option key={unidad.id} value={unidad.id}>
                      {unidad.nombre}
                    </option>
                  ))}
                </select>
              </label>{" "}
              <button
                type="button"
                onClick={() => eliminarLinea(linea.key)}
                disabled={lineas.length === 1}
              >
                Quitar insumo
              </button>
            </p>
          </div>
        ))}

        <p>
          <button type="button" onClick={agregarLinea}>
            Agregar insumo
          </button>{" "}
          <button type="submit" disabled={guardando}>
            {guardando ? "Guardando..." : "Registrar consumo"}
          </button>
        </p>

        <p>
          <small>
            El consumo se registra como egreso de mercadería (ventaId NULL) junto con el
            consumo personal en una sola transacción. Si algo falla, no se guarda nada.
          </small>
        </p>
      </form>
    </div>
  );
}
