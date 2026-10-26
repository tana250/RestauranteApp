import api from "./api";

export const getAll = (params = {}) => api.get("/ingresoMercaderia/", { params });
export const getById = (id) => api.get("/ingresoMercaderia/" + id);
export const create = (data) => api.post("/ingresoMercaderia/", data);
export const update = (id, data) => api.patch("/ingresoMercaderia/" + id, data);
export const remove = (id) => api.delete("/ingresoMercaderia/" + id);
