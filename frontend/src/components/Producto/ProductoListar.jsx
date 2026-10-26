import useProducto from "../../hooks/useProducto";

export default function ProductoListar({
  onEdit,
  onSelect,
  selectedId,
  items: itemsProp,
  onRemove,
  onToggleActivo,
}) {
  const producto = useProducto({ autoFetch: itemsProp === undefined });
  const items = itemsProp ?? producto.items;
  const remove = onRemove ?? producto.remove;
  const toggleActivo = onToggleActivo ?? producto.toggleActivo;

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
          <tr
            key={item.id}
            onClick={() => onSelect && onSelect(item)}
            style={{
              cursor: onSelect ? "pointer" : "default",
              background: selectedId === item.id ? "var(--accent-bg)" : undefined,
            }}
          >
            <td>{item.id}</td>
            <td>{item.nombre}</td>
            <td>{item.valor}</td>
            <td>{item.activo ? "Si" : "No"}</td>
            <td>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleActivo(item);
                }}
              >
                {item.activo ? "Desactivar" : "Activar"}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (onEdit) onEdit(item);
                }}
              >
                Editar
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  remove(item.id);
                }}
              >
                Eliminar
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
