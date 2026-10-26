import useMetodosPago from "../../hooks/useMetodosPago";

export default function MetodosPagoListar({ onEdit }) {
  const { items, remove } = useMetodosPago();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Metodo</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.metodo}</td>
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
