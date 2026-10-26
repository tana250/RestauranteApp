import api from "./api";

export const getAll = (params = {}) => api.get("/insumos/", { params });
export const getById = (id) => api.get("/insumos/" + id);
export const create = (data) => api.post("/insumos/", data);
export const update = (id, data) => api.patch("/insumos/" + id, data);
export const remove = (id) => api.delete("/insumos/" + id);
