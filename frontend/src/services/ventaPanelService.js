import api from "./api";

export const guardar = (data) => api.post("/venta/guardar", data);
export const getDetalle = (id) => api.get(`/venta/${id}/detalle`);
