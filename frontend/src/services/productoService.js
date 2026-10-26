import api from "./api";

export const getAll = (params = {}) => api.get("/producto/", { params });
export const getById = (id) => api.get("/producto/" + id);
export const create = (data) => api.post("/producto/", data);
export const update = (id, data) => api.patch("/producto/" + id, data);
export const remove = (id) => api.delete("/producto/" + id);
