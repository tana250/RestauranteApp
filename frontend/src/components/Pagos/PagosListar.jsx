import usePagos from "../../hooks/usePagos";

export default function PagosListar({ onEdit }) {
  const { items, remove } = usePagos();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Datos</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td><pre>{JSON.stringify(item)}</pre></td>
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
