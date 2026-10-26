import api from "./api";

export const getAll = (params = {}) => api.get("/pagos/", { params });
export const getById = (id) => api.get("/pagos/" + id);
export const create = (data) => api.post("/pagos/", data);
export const update = (id, data) => api.patch("/pagos/" + id, data);
export const remove = (id) => api.delete("/pagos/" + id);
