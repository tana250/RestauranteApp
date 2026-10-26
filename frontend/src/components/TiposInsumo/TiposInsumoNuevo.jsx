import { useState } from "react";
import useTiposInsumo from "../../hooks/useTiposInsumo";

export default function TiposInsumoNuevo({ onCreated }) {
  const { create } = useTiposInsumo();
  const [tipo, setTipo] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ tipo });
    setTipo("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={tipo} onChange={(e) => setTipo(e.target.value)} placeholder="tipo" required />
      <button type="submit">Guardar</button>
    </form>
  );
}
