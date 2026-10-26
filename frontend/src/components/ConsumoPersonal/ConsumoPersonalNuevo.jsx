import { useState } from "react";
import useConsumoPersonal from "../../hooks/useConsumoPersonal";

export default function ConsumoPersonalNuevo({ onCreated }) {
  const { create } = useConsumoPersonal();
  const [json, setJson] = useState("{}");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(json);
      await create(data);
      setJson("{}");
      if (onCreated) onCreated();
    } catch (err) {
      alert("JSON invalido");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea value={json} onChange={(e) => setJson(e.target.value)} placeholder='{"campo":"valor"}' />
      <button type="submit">Guardar</button>
    </form>
  );
}
