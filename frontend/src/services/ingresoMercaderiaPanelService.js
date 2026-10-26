import api from "./api";

export const guardar = (data) => api.post("/ingresoMercaderia/guardar", data);
