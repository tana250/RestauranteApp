import api from "./api";

export const getAll = (params = {}) => api.get("/venta/", { params });
export const getById = (id) => api.get("/venta/" + id);
export const create = (data) => api.post("/venta/", data);
export const update = (id, data) => api.patch("/venta/" + id, data);
export const remove = (id) => api.delete("/venta/" + id);
