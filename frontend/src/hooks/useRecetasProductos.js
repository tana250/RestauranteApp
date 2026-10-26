import { useEffect, useState } from "react";
import * as service from "../services/recetasProductosService";

export default function useRecetasProductos() {
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

  const remove = async (id) => {
    await service.remove(id);
    await fetchAll();
  };

  useEffect(() => {
    fetchAll();
  }, []);

  return { items, loading, fetchAll, create, update, remove };
}
