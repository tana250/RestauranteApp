import { useState } from "react";
import useMarcas from "../../hooks/useMarcas";

export default function MarcasNuevo({ onCreated }) {
  const { create } = useMarcas();
  const [nombre, setNombre] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ nombre });
    setNombre("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="nombre" required />
      <button type="submit">Guardar</button>
    </form>
  );
}
