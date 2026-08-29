// Configuración central del panel de tienda.
// API_BASE apunta al API Gateway.
//
// Local:   http://localhost:5000
// Render:  cámbialo por la URL de tu gateway desplegado, p. ej.
//          https://sfa-gateway.onrender.com
// También puedes definir window.API_BASE antes de cargar este archivo
// (en un <script> previo) para anular este valor sin editar nada.

const API_BASE =
  (typeof window !== "undefined" && window.API_BASE) || "http://localhost:5000";