import { useState } from "react";
import useMozo from "../../hooks/useMozo";

export default function MozoNuevo({ onCreated }) {
  const { create } = useMozo();
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
