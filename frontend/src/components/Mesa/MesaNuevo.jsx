import { useState } from "react";
import useMesa from "../../hooks/useMesa";

export default function MesaNuevo({ onCreated }) {
  const { create } = useMesa();
  const [numero, setNumero] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ numero: Number(numero) });
    setNumero("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="number" value={numero} onChange={(e) => setNumero(e.target.value)} placeholder="numero" required />
      <button type="submit">Guardar</button>
    </form>
  );
}
