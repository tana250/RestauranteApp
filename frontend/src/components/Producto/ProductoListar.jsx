import useProducto from "../../hooks/useProducto";

export default function ProductoListar({ onEdit }) {
  const { items, remove, toggleActivo } = useProducto();

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Valor</th>
          <th>Activo</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.nombre}</td>
            <td>{item.valor}</td>
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
