// Pantalla 2: catálogo y personalización.
// Consume GET /pedidos/api/tiendas/<id>/productos y mantiene el carrito
// en memoria + sessionStorage (para sobrevivir a la navegación a checkout).

document.addEventListener("DOMContentLoaded", () => {
  const tiendaId = sessionStorage.getItem("tienda_id");
  const tiendaNombre = sessionStorage.getItem("tienda_nombre");

  if (!tiendaId) {
    window.location.href = "index.html";
    return;
  }

  const tiendaActual = document.getElementById("tienda-actual");
  tiendaActual.textContent = tiendaNombre || `Tienda #${tiendaId}`;
  tiendaActual.classList.add("visible");

  const grid = document.getElementById("productos-grid");
  const mensajeError = document.getElementById("mensaje-error");
  const cargando = document.getElementById("cargando");
  const botonCarrito = document.getElementById("barra-carrito");
  const resumenCarrito = document.getElementById("carrito-resumen");
  const btnIrCheckout = document.getElementById("btn-ir-checkout");

  let productos = [];
  let tipoActivo = "torta";

  // ---- Carrito (memoria + sessionStorage) --------------------
  const leerCarrito = () => {
    try {
      return JSON.parse(sessionStorage.getItem("carrito") || "[]");
    } catch {
      return [];
    }
  };
  const escribirCarrito = (carrito) => {
    sessionStorage.setItem("carrito", JSON.stringify(carrito));
    actualizarBarra(carrito);
  };

  const actualizarBarra = (carrito) => {
    const cantidad = carrito.reduce((total, item) => total + item.cantidad, 0);
    if (cantidad === 0) {
      botonCarrito.style.display = "none";
      botonCarrito.previousElementSibling.classList.add("vacio");
      botonCarrito.previousElementSibling.textContent =
        "Aún no has agregado productos a tu pedido.";
      return;
    }
    resumenCarrito.textContent = `${cantidad} producto(s)`;
    botonCarrito.style.display = "flex";
  };

  // ---- Render del catálogo ------------------------------------
  const renderProductos = () => {
    const filtrados = productos.filter(
      (producto) => producto.tipo === tipoActivo
    );

    if (filtrados.length === 0) {
      grid.innerHTML = '<div class="vacio">No hay productos en esta categoría.</div>';
      return;
    }

    grid.innerHTML = "";
    filtrados.forEach((producto) => {
      const tarjeta = document.createElement("div");
      tarjeta.className = `tarjeta-producto ${producto.tipo}`;

      const textoClase = producto.tipo === "torta" ? "TORTAS" : "BOCADITOS";
      const imagen = producto.imagen_url || "";

      const portada = imagen
        ? `<div class="portada con-imagen"><img src="${imagen}" alt="${producto.nombre}" loading="lazy" /><span>${textoClase}</span></div>`
        : `<div class="portada"><span>${textoClase}</span></div>`;

      tarjeta.innerHTML = `
        ${portada}
        <div class="cuerpo">
          <div>
            <div class="nombre">${producto.nombre}</div>
            <div class="descripcion">${producto.descripcion}</div>
          </div>
          <div class="precio">S/ ${Number(producto.precio_base).toFixed(2)}</div>
          <div class="opciones">
            <select class="sel-tamano" title="Tamaño">
              ${producto.tamanos
                .map((tamano) => `<option value="${tamano}">${tamano}</option>`)
                .join("")}
            </select>
            <select class="sel-sabor" title="Sabor">
              ${producto.sabores
                .map((sabor) => `<option value="${sabor}">${sabor}</option>`)
                .join("")}
            </select>
          </div>
          <div class="grupo">
            <label class="fila-cantidad">Cantidad</label>
            <input type="number" class="inp-cantidad" value="1" min="1" max="50" />
          </div>
          <button class="agregar" data-id="${producto.id}">Agregar al pedido</button>
        </div>
      `;

      const botonAgregar = tarjeta.querySelector(".agregar");
      botonAgregar.addEventListener("click", () => {
        const tamano = tarjeta.querySelector(".sel-tamano").value;
        const sabor = tarjeta.querySelector(".sel-sabor").value;
        const cantidad = Math.max(
          1,
          parseInt(tarjeta.querySelector(".inp-cantidad").value, 10) || 1
        );

        const carrito = leerCarrito();
        const existente = carrito.find(
          (item) =>
            item.producto_id === producto.id &&
            item.tamano === tamano &&
            item.sabor === sabor
        );

        if (existente) {
          existente.cantidad += cantidad;
        } else {
          carrito.push({
            producto_id: producto.id,
            nombre: producto.nombre,
            precio_base: producto.precio_base,
            cantidad,
            tamano,
            sabor,
          });
        }
        escribirCarrito(carrito);
      });

      grid.appendChild(tarjeta);
    });
  };

  const mostrarError = (texto) => {
    cargando.style.display = "none";
    mensajeError.textContent = texto;
    mensajeError.classList.add("visible");
  };

  // ---- Tabs Tortas / Bocaditos --------------------------------
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("activo"));
      tab.classList.add("activo");
      tipoActivo = tab.dataset.tipo;
      renderProductos();
    });
  });

  // ---- Navegación a checkout -----------------------------------
  btnIrCheckout.addEventListener("click", () => {
    window.location.href = "checkout.html";
  });

  // ---- Inicialización ------------------------------------------
  actualizarBarra(leerCarrito());

  fetch(`${API_BASE}/pedidos/api/tiendas/${tiendaId}/productos`)
    .then((respuesta) => {
      if (!respuesta.ok) {
        throw new Error(`Error HTTP ${respuesta.status}`);
      }
      return respuesta.json();
    })
    .then((data) => {
      cargando.style.display = "none";
      productos = data || [];
      renderProductos();
    })
    .catch((error) => {
      console.error("Error al cargar el catálogo:", error);
      mostrarError(
        "No se pudo cargar el catálogo. Verifica que el API Gateway y el microservicio de pedidos estén activos."
      );
    });
});