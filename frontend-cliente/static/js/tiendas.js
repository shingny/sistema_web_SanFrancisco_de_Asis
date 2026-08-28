// Pantalla 1: selección de tienda.
// Al hacer clic guarda tienda_id en sessionStorage y navega al catálogo.

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tiendas-grid");
  const mensajeError = document.getElementById("mensaje-error");
  const cargando = document.getElementById("cargando");

  const mostrarError = (texto) => {
    cargando.style.display = "none";
    mensajeError.textContent = texto;
    mensajeError.classList.add("visible");
  };

  const crearTarjeta = (tienda) => {
    const tarjeta = document.createElement("div");
    tarjeta.className = "tarjeta-tienda";
    tarjeta.tabIndex = 0;
    tarjeta.setAttribute("role", "button");
    tarjeta.setAttribute("aria-label", `Seleccionar ${tienda.nombre}`);

    const abierto = tienda.estado === "abierto";
    const etiquetaEstado = abierto ? "Abierto" : "Cerrado";

    tarjeta.innerHTML = `
      <span class="nombre">${tienda.nombre}</span>
      <span class="zona">${tienda.zona}</span>
      <span class="direccion">${tienda.direccion}</span>
      <span class="horario">Horario: ${tienda.horario}</span>
      <span class="horario">
        <span class="estado-dot ${abierto ? "abierto" : ""}"></span>${etiquetaEstado}
      </span>
    `;

    const seleccionar = () => {
      // Guarda la tienda elegida y navega al catálogo
      sessionStorage.setItem("tienda_id", tienda.id);
      sessionStorage.setItem("tienda_nombre", tienda.nombre);
      window.location.href = "catalogo.html";
    };

    tarjeta.addEventListener("click", seleccionar);
    tarjeta.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        seleccionar();
      }
    });

    return tarjeta;
  };

  fetch(`${API_BASE}/pedidos/api/tiendas`)
    .then((respuesta) => {
      if (!respuesta.ok) {
        throw new Error(`Error HTTP ${respuesta.status}`);
      }
      return respuesta.json();
    })
    .then((tiendas) => {
      cargando.style.display = "none";
      if (!tiendas || tiendas.length === 0) {
        grid.innerHTML = '<div class="vacio">No hay tiendas disponibles por ahora.</div>';
        return;
      }
      tiendas.forEach((tienda) => grid.appendChild(crearTarjeta(tienda)));
    })
    .catch((error) => {
      console.error("Error al cargar tiendas:", error);
      mostrarError(
        "No se pudieron cargar las tiendas. Verifica que el API Gateway y los microservicios estén activos."
      );
    });
});