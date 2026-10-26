import api from "./api";

export const getAll = (params = {}) => api.get("/unidadesMedida/", { params });
export const getById = (id) => api.get("/unidadesMedida/" + id);
export const create = (data) => api.post("/unidadesMedida/", data);
export const update = (id, data) => api.patch("/unidadesMedida/" + id, data);
export const remove = (id) => api.delete("/unidadesMedida/" + id);
