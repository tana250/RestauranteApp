import api from "./api";

export const getAll = (params = {}) => api.get("/mesa/", { params });
export const getById = (id) => api.get("/mesa/" + id);
export const create = (data) => api.post("/mesa/", data);
export const update = (id, data) => api.patch("/mesa/" + id, data);
export const remove = (id) => api.delete("/mesa/" + id);
