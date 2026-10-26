import { useEffect, useState } from "react";
import * as service from "../services/productoService";

export default function useProducto({ autoFetch = true } = {}) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAll = async (params = {}) => {
    setLoading(true);
    try {
      const res = await service.getAll(params);
      setItems(res.data);
    } finally {
      setLoading(false);
    }
  };

  const create = async (data) => {
    const res = await service.create(data);
    await fetchAll();
    return res.data;
  };

  const update = async (id, data) => {
    const res = await service.update(id, data);
    await fetchAll();
    return res.data;
  };

  const toggleActivo = async (item) => {
    await service.update(item.id, { activo: !item.activo });
    await fetchAll();
  };

  const remove = async (id) => {
    await service.remove(id);
    await fetchAll();
  };

  useEffect(() => {
    if (autoFetch) fetchAll();
  }, [autoFetch]);

  return { items, loading, fetchAll, create, update, toggleActivo, remove };
}
