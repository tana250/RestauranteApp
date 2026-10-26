import api from "./api";

export const guardar = (data) => api.patch("/insumos/guardar", data);
