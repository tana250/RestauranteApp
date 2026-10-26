import api from "./api";

export const getAll = (params = {}) => api.get("/tiposInsumo/", { params });
export const getById = (id) => api.get("/tiposInsumo/" + id);
export const create = (data) => api.post("/tiposInsumo/", data);
export const update = (id, data) => api.patch("/tiposInsumo/" + id, data);
export const remove = (id) => api.delete("/tiposInsumo/" + id);
