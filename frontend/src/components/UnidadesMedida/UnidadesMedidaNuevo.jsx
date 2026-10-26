import { useState } from "react";
import useUnidadesMedida from "../../hooks/useUnidadesMedida";

export default function UnidadesMedidaNuevo({ onCreated }) {
  const { create } = useUnidadesMedida();
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
