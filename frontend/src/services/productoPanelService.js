import api from "./api";

export const guardar = (data) => api.post("/producto/guardar", data);
export const getDetalle = (id) => api.get("/producto/" + id + "/detalle");
