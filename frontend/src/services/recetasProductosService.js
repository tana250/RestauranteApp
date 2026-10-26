import api from "./api";

export const getAll = (params = {}) => api.get("/recetasProductos/", { params });
export const getById = (id) => api.get("/recetasProductos/" + id);
export const create = (data) => api.post("/recetasProductos/", data);
export const update = (id, data) => api.patch("/recetasProductos/" + id, data);
export const remove = (id) => api.delete("/recetasProductos/" + id);
