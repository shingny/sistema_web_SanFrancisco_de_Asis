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
  const btnVolver = document.getElementById("btn-volver");
  tiendaActual.textContent = tiendaNombre || `Tienda #${tiendaId}`;
  tiendaActual.classList.add("visible");
  document.getElementById("marca-titulo").textContent =
    tiendaNombre || `Tienda #${tiendaId}`;

  if (btnVolver) {
    btnVolver.addEventListener("click", () => {
      window.location.href = "index.html";
    });
  }

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
        ? `<div class="portada con-imagen"><img src="${imagen}" alt="${producto.nombre}" loading="lazy" /><span class="chip-tipo">${textoClase}</span></div>`
        : `<div class="portada sin-imagen"><span class="chip-tipo">${textoClase}</span><span class="icono-bocado">${producto.tipo === "torta" ? "🎂" : "🍪"}</span></div>`;

      const chipsTamano = (producto.tamanos || [])
        .map((t, i) => `<button type="button" class="chip sel-tamano ${i === 0 ? "activo" : ""}" data-valor="${t}">${t}</button>`)
        .join("");
      const chipsSabor = (producto.sabores || [])
        .map((s, i) => `<button type="button" class="chip sel-sabor ${i === 0 ? "activo" : ""}" data-valor="${s}">${s}</button>`)
        .join("");

      tarjeta.innerHTML = `
        ${portada}
        <div class="cuerpo">
          <div class="nombre">${producto.nombre}</div>
          <div class="descripcion">${producto.descripcion}</div>
          <div class="fila-precio-agregar">
            <div class="precio">S/ ${Number(producto.precio_base).toFixed(2)}</div>
            <button class="agregar" data-id="${producto.id}">+ Agregar</button>
          </div>
          ${chipsTamano ? `<div class="campo-chip"><label>Tamaño</label><div class="chips">${chipsTamano}</div></div>` : ""}
          ${chipsSabor ? `<div class="campo-chip"><label>Sabor</label><div class="chips">${chipsSabor}</div></div>` : ""}
        </div>
      `;

      // Selección de chips de tamaño / sabor
      tarjeta.querySelectorAll(".sel-tamano").forEach((c) =>
        c.addEventListener("click", () => {
          tarjeta.querySelectorAll(".sel-tamano").forEach((x) => x.classList.remove("activo"));
          c.classList.add("activo");
        })
      );
      tarjeta.querySelectorAll(".sel-sabor").forEach((c) =>
        c.addEventListener("click", () => {
          tarjeta.querySelectorAll(".sel-sabor").forEach((x) => x.classList.remove("activo"));
          c.classList.add("activo");
        })
      );

      const botonAgregar = tarjeta.querySelector(".agregar");
      botonAgregar.addEventListener("click", () => {
        const selTamano = tarjeta.querySelector(".sel-tamano.activo");
        const selSabor = tarjeta.querySelector(".sel-sabor.activo");
        const tamano = selTamano ? selTamano.dataset.valor : "";
        const sabor = selSabor ? selSabor.dataset.valor : "";
        const cantidad = 1;

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