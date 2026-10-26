import { useState } from "react";
import useProveedor from "../../hooks/useProveedor";

export default function ProveedorNuevo({ onCreated }) {
  const { create } = useProveedor();
  const [nombre, setNombre] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ nombre });
    setNombre("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Nombre" required />
      <button type="submit">Guardar</button>
    </form>
  );
}
