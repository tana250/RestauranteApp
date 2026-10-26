import api from "./api";

export const getAll = (params = {}) => api.get("/consumoPersonal/", { params });
export const getById = (id) => api.get("/consumoPersonal/" + id);
export const create = (data) => api.post("/consumoPersonal/", data);
export const update = (id, data) => api.patch("/consumoPersonal/" + id, data);
export const remove = (id) => api.delete("/consumoPersonal/" + id);
