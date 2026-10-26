import api from "./api";

export const getAll = (params = {}) => api.get("/egresoMercaderia/", { params });
export const getById = (id) => api.get("/egresoMercaderia/" + id);
export const create = (data) => api.post("/egresoMercaderia/", data);
export const update = (id, data) => api.patch("/egresoMercaderia/" + id, data);
export const remove = (id) => api.delete("/egresoMercaderia/" + id);
