import useMozo from "../../hooks/useMozo";

export default function MozoListar({ onEdit }) {
  const { items, remove } = useMozo();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Personal</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.personalNombre || `Personal #${item.personalId}`}</td>
            <td>
              <button onClick={() => onEdit && onEdit(item)}>Editar</button>
              <button onClick={() => remove(item.id)}>Eliminar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
