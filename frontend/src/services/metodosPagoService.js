import api from "./api";

export const getAll = (params = {}) => api.get("/metodosPago/", { params });
export const getById = (id) => api.get("/metodosPago/" + id);
export const create = (data) => api.post("/metodosPago/", data);
export const update = (id, data) => api.patch("/metodosPago/" + id, data);
export const remove = (id) => api.delete("/metodosPago/" + id);
