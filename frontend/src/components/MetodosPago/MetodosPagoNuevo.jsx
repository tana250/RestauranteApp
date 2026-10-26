import { useState } from "react";
import useMetodosPago from "../../hooks/useMetodosPago";

export default function MetodosPagoNuevo({ onCreated }) {
  const { create } = useMetodosPago();
  const [metodo, setMetodo] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ metodo });
    setMetodo("");
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={metodo} onChange={(e) => setMetodo(e.target.value)} placeholder="Metodo" required />
      <button type="submit">Guardar</button>
    </form>
  );
}
