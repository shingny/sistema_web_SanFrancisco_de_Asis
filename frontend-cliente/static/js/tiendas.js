// Pantalla 1: selección de tienda.
// Al hacer clic resalta la tienda elegida y navega al catálogo.

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tiendas-grid");
  const mensajeError = document.getElementById("mensaje-error");
  const cargando = document.getElementById("cargando");
  const notaSeleccion = document.querySelector(".nota-seleccion");

  const mostrarError = (texto) => {
    cargando.style.display = "none";
    if (notaSeleccion) notaSeleccion.style.display = "none";
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
    const etiquetaEstado = abierto ? "Abierto ahora" : "Cerrado";

    tarjeta.innerHTML = `
      <span class="icono-tienda">🏪</span>
      <div class="info-tienda">
        <span class="nombre">${tienda.nombre}</span>
        <span class="direccion">${tienda.direccion}</span>
        <span class="zona">${tienda.zona}</span>
      </div>
      <div class="lado-estado">
        <span class="estado-tag ${abierto ? "abierto" : "cerrado"}">
          <span class="estado-dot ${abierto ? "abierto" : ""}"></span>${etiquetaEstado}
        </span>
        <span class="flecha">›</span>
      </div>
    `;

    const seleccionar = () => {
      // Resalta la selección con borde y fondo naranja claro
      document
        .querySelectorAll(".tarjeta-tienda")
        .forEach((t) => t.classList.remove("seleccionada"));
      tarjeta.classList.add("seleccionada");

      // Pequeño retraso para que se aprecie el resaltado antes de navegar
      setTimeout(() => {
        sessionStorage.setItem("tienda_id", tienda.id);
        sessionStorage.setItem("tienda_nombre", tienda.nombre);
        window.location.href = "catalogo.html";
      }, 260);
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
        grid.innerHTML =
          '<div class="vacio">No hay tiendas disponibles por ahora.</div>';
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
