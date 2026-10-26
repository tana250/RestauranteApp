import { useState } from "react";
import usePersonal from "../../hooks/usePersonal";

export default function PersonalNuevo({ onCreated }) {
  const { create } = usePersonal();
  const [dni, setDni] = useState("");
  const [nombre, setNombre] = useState("");
  const [activo, setActivo] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ dni, nombre, activo });
    setDni("");
    setNombre("");
    setActivo(true);
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={dni} onChange={(e) => setDni(e.target.value)} placeholder="DNI" required />
      <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Nombre" required />
      <label>
        <input type="checkbox" checked={activo} onChange={(e) => setActivo(e.target.checked)} /> Activo
      </label>
      <button type="submit">Guardar</button>
    </form>
  );
}
