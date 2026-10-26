import { useState } from "react";
import useMozo from "../../hooks/useMozo";
import usePersonal from "../../hooks/usePersonal";

export default function MozoNuevo({ onCreated }) {
  const { create } = useMozo();
  const { items: personales, loading: cargandoPersonales } = usePersonal();
  const [personalId, setPersonalId] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ personalId: Number(personalId) });
    setPersonalId("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Personal:{" "}
        <select
          value={personalId}
          onChange={(e) => setPersonalId(e.target.value)}
          required
        >
          <option value="">Seleccione...</option>
          {personales.map((personal) => (
            <option key={personal.id} value={personal.id}>
              {personal.nombre}
            </option>
          ))}
        </select>
      </label>
      {cargandoPersonales && <p>Cargando personales...</p>}
      <button type="submit">Guardar</button>
    </form>
  );
}
