import usePersonal from "../../hooks/usePersonal";

export default function PersonalListar({ onEdit }) {
  const { items, remove, toggleActivo } = usePersonal();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>DNI</th>
          <th>Nombre</th>
          <th>Activo</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.dni}</td>
            <td>{item.nombre}</td>
            <td>{item.activo ? "Si" : "No"}</td>
            <td>
              <button onClick={() => toggleActivo(item)}>{item.activo ? "Desactivar" : "Activar"}</button>
              <button onClick={() => onEdit && onEdit(item)}>Editar</button>
              <button onClick={() => remove(item.id)}>Eliminar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
