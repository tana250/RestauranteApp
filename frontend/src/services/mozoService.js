import api from "./api";

export const getAll = (params = {}) => api.get("/mozo/", { params });
export const getById = (id) => api.get("/mozo/" + id);
export const create = (data) => api.post("/mozo/", data);
export const update = (id, data) => api.patch("/mozo/" + id, data);
export const remove = (id) => api.delete("/mozo/" + id);
