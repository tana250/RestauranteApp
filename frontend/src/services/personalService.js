import api from "./api";

export const getAll = (params = {}) => api.get("/personal/", { params });
export const getById = (id) => api.get("/personal/" + id);
export const create = (data) => api.post("/personal/", data);
export const update = (id, data) => api.patch("/personal/" + id, data);
export const remove = (id) => api.delete("/personal/" + id);
