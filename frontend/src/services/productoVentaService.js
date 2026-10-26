import api from "./api";

export const getAll = (params = {}) => api.get("/productoVenta/", { params });
export const getById = (id) => api.get("/productoVenta/" + id);
export const create = (data) => api.post("/productoVenta/", data);
export const update = (id, data) => api.patch("/productoVenta/" + id, data);
export const remove = (id) => api.delete("/productoVenta/" + id);
