import api from "./api";

export const getAll = (params = {}) => api.get("/marcas/", { params });
export const getById = (id) => api.get("/marcas/" + id);
export const create = (data) => api.post("/marcas/", data);
export const update = (id, data) => api.patch("/marcas/" + id, data);
export const remove = (id) => api.delete("/marcas/" + id);
