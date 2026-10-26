import api from "./api";

export const getAll = (params = {}) => api.get("/proveedor/", { params });
export const getById = (id) => api.get("/proveedor/" + id);
export const create = (data) => api.post("/proveedor/", data);
export const update = (id, data) => api.patch("/proveedor/" + id, data);
export const remove = (id) => api.delete("/proveedor/" + id);
