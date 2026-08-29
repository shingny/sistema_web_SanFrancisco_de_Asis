// Pantalla 3: checkout — datos del cliente y confirmación.
// Hace POST /pedidos/api/pedidos y muestra el número de pedido.

document.addEventListener("DOMContentLoaded", () => {
  const tiendaId = sessionStorage.getItem("tienda_id");
  const tiendaNombre = sessionStorage.getItem("tienda_nombre");

  if (!tiendaId) {
    window.location.href = "index.html";
    return;
  }

  document.getElementById("tienda-actual").textContent =
    tiendaNombre || `Tienda #${tiendaId}`;
  document.getElementById("tienda-actual").classList.add("visible");

  const btnVolver = document.getElementById("btn-volver");
  if (btnVolver) {
    btnVolver.addEventListener("click", () => {
      window.location.href = "catalogo.html";
    });
  }

  // ---- Chips de método de pago --------------------------------
  const chipsPago = document.querySelectorAll(".chip-pago");
  chipsPago.forEach((chip) => {
    chip.addEventListener("click", () => {
      chipsPago.forEach((c) => c.classList.remove("activo"));
      chip.classList.add("activo");
      document.getElementById("metodo_pago").value = chip.dataset.metodo;
    });
  });

  const leerCarrito = () => {
    try {
      return JSON.parse(sessionStorage.getItem("carrito") || "[]");
    } catch {
      return [];
    }
  };

  const carrito = leerCarrito();
  if (carrito.length === 0) {
    window.location.href = "catalogo.html";
    return;
  }

  const mensajeError = document.getElementById("mensaje-error");
  const resumenItems = document.getElementById("resumen-items");
  const resumenTotal = document.getElementById("resumen-total");
  const btnConfirmar = document.getElementById("btn-confirmar");
  const formulario = document.getElementById("form-checkout");

  // ---- Resumen del pedido --------------------------------------
  const total = carrito.reduce(
    (suma, item) => suma + Number(item.precio_base || 0) * item.cantidad,
    0
  );

  resumenItems.innerHTML = carrito
    .map((item) => {
      const opciones = [item.tamano, item.sabor]
        .filter((valor) => valor)
        .join(" · ");
      return `
        <div class="item-resumen">
          <div class="detalle">
            ${item.cantidad} x ${item.nombre}
            ${opciones ? `<div class="sub">${opciones}</div>` : ""}
          </div>
          <div>S/ ${(Number(item.precio_base) * item.cantidad).toFixed(2)}</div>
        </div>
      `;
    })
    .join("");

  resumenTotal.textContent = `S/ ${total.toFixed(2)}`;

  // ---- Establecer fecha mínima (hoy) ---------------------------
  const inputFecha = document.getElementById("fecha_entrega");
  if (inputFecha) {
    inputFecha.min = new Date().toISOString().split("T")[0];
  }

  // ---- Envío del pedido -----------------------------------------
  formulario.addEventListener("submit", (event) => {
    event.preventDefault();

    const nombre = document.getElementById("nombre").value.trim();
    const celular = document.getElementById("celular").value.trim();
    const email = document.getElementById("email").value.trim();
    const fechaEntrega = document.getElementById("fecha_entrega").value;
    const metodoPago = document.getElementById("metodo_pago").value;
    const mensaje = document.getElementById("mensaje").value.trim();

    if (!nombre || !celular) {
      mensajeError.textContent = "Por favor completa tu nombre y celular.";
      mensajeError.classList.add("visible");
      return;
    }

    btnConfirmar.disabled = true;
    btnConfirmar.textContent = "Enviando pedido...";

    const payload = {
      tienda_id: Number(tiendaId),
      cliente: { nombre, celular, email },
      items: carrito.map((item) => ({
        producto_id: item.producto_id,
        cantidad: item.cantidad,
        tamano: item.tamano,
        sabor: item.sabor,
      })),
      fecha_entrega: fechaEntrega || null,
      metodo_pago: metodoPago,
      mensaje,
    };

    fetch(`${API_BASE}/pedidos/api/pedidos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(async (respuesta) => {
        const data = await respuesta.json();
        if (!respuesta.ok) {
          throw new Error(
            Array.isArray(data.error)
              ? data.error.join(" · ")
              : data.error || "Error al registrar el pedido"
          );
        }
        return data;
      })
      .then((pedido) => {
        // Limpia el carrito y muestra la confirmación
        sessionStorage.removeItem("carrito");
        document.getElementById("nro-pedido").textContent = `#${pedido.id}`;
        formulario.style.display = "none";
        document.getElementById("vista-confirmacion").style.display = "block";
        window.scrollTo({ top: 0, behavior: "smooth" });

        // Muestra el toast de confirmación
        const toast = document.getElementById("toast-confirmacion");
        if (toast) {
          toast.style.display = "flex";
          setTimeout(() => {
            toast.classList.add("oculto");
            setTimeout(() => {
              toast.style.display = "none";
              toast.classList.remove("oculto");
            }, 400);
          }, 3000);
        }
      })
      .catch((error) => {
        console.error("Error al confirmar pedido:", error);
        mensajeError.textContent = error.message;
        mensajeError.classList.add("visible");
        btnConfirmar.disabled = false;
        btnConfirmar.textContent = "Confirmar pedido";
      });
  });
});