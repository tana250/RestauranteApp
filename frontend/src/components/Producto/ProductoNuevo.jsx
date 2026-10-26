import { useState } from "react";
import useProducto from "../../hooks/useProducto";

export default function ProductoNuevo({ onCreated }) {
  const { create } = useProducto();
  const [nombre, setNombre] = useState("");
  const [valor, setValor] = useState("");
  const [activo, setActivo] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await create({ nombre, valor: Number(valor), activo });
    setNombre("");
    setValor("");
    setActivo(true);
    if (onCreated) onCreated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Nombre" required />
      <input type="number" value={valor} onChange={(e) => setValor(e.target.value)} placeholder="Valor" required />
      <label>
        <input type="checkbox" checked={activo} onChange={(e) => setActivo(e.target.checked)} /> Activo
      </label>
      <button type="submit">Guardar</button>
    </form>
  );
}
