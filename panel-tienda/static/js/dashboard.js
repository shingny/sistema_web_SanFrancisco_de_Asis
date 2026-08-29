// Dashboard del panel de tienda:
//  - Kanban de pedidos (Microservicio 1)
//  - Kanban de separado/reservas (Microservicio 2)
//  - Notificaciones en tiempo real (polling 12s) + toasts

document.addEventListener("DOMContentLoaded", () => {
  const token = sessionStorage.getItem("panel_token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // ---------- Configuración y utilidades ----------
  const selectTienda = document.getElementById("select-tienda");
  const mensajeError = document.getElementById("mensaje-error");
  const toastArea = document.getElementById("toast-area");
  const URL_PEDIDOS = `${API_BASE}/pedidos/api`;
  const URL_RESERVAS = `${API_BASE}/reservas/api`;

  // Muestra el usuario en la barra lateral
  const usuarioSidebar = document.getElementById("panel-usuario");
  if (usuarioSidebar) {
    usuarioSidebar.textContent =
      sessionStorage.getItem("panel_usuario") || "Personal";
  }

  // Actualiza las tarjetas de estadísticas del dashboard
  const actualizarStats = () => {
    const todos = document.querySelectorAll(".columna[data-estado]");
    todos.forEach((columna) => {
      const estado = columna.dataset.estado;
      const valor = Number(
        columna.querySelector(".contador")?.textContent || "0"
      );
      const celda = document.querySelector(
        `[data-contador-stat="${CSS.escape(estado)}"]`
      );
      if (celda) celda.textContent = valor;
    });
  };

  const cabeceras = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  });

  const mostrarError = (texto) => {
    mensajeError.textContent = texto;
    mensajeError.classList.add("visible");
  };

  const ocultarError = () => mensajeError.classList.remove("visible");

  // Avances permitidos por ciclo de vida
  const FLUJO_PEDIDO = ["nuevo", "en_preparacion", "listo", "entregado"];
  const FLUJO_RESERVA = ["reservado", "en_preparacion", "listo_para_recojo", "entregado"];

  const ETIQUETAS_PEDIDO = {
    nuevo: "Nuevo",
    en_preparacion: "En preparación",
    listo: "Listo para recojo",
    entregado: "Entregado",
  };

  const ETIQUETAS_RESERVA = {
    reservado: "Reservado",
    en_preparacion: "En preparación",
    listo_para_recojo: "Listo para recojo",
    entregado: "Entregado",
  };

  const estadoSiguiente = (estado, flujo) => {
    const indice = flujo.indexOf(estado);
    if (indice === -1 || indice === flujo.length - 1) return null;
    return flujo[indice + 1];
  };

  // Estado en memoria para detectar pedidos/reservas nuevos
  const estadoLocal = {
    pedidos: [],     // ids de pedidos ya conocidos
    reservas: [],    // ids de reservas ya conocidas
    tiendaId: null,
  };

  // ---------- Notificaciones (polling) ----------
  const mostrarToast = (titulo, detalle) => {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<strong>${titulo}</strong><br />${detalle}`;
    toastArea.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
  };

  const verificarNuevosPedidos = async () => {
    const tiendaId = estadoLocal.tiendaId;
    if (!tiendaId) return;

    try {
      const respuesta = await fetch(
        `${URL_PEDIDOS}/pedidos?tienda_id=${tiendaId}&estado=nuevo`,
        { headers: cabeceras() }
      );
      if (!respuesta.ok) throw new Error("Error al consultar pedidos nuevos");
      const pedidos = await respuesta.json();

      pedidos.forEach((pedido) => {
        if (!estadoLocal.pedidos.includes(pedido.id)) {
          estadoLocal.pedidos.push(pedido.id);
          const productos = (pedido.items || [])
            .map((item) => `${item.cantidad} x ${item.nombre}`)
            .join(", ");
          mostrarToast(
            `Nuevo pedido #${pedido.id}`,
            `${pedido.cliente ? pedido.cliente.nombre : "Cliente"} · ${productos}`
          );
        }
      });
    } catch (error) {
      console.error("Polling de pedidos:", error);
    }
  };

  // ---------- Carga del selector de tiendas ----------
  const cargarTiendas = async () => {
    try {
      const respuesta = await fetch(`${URL_PEDIDOS}/tiendas`);
      if (!respuesta.ok) throw new Error("Error al cargar tiendas");
      const tiendas = await respuesta.json();

      selectTienda.innerHTML = "";
      tiendas.forEach((tienda) => {
        const opcion = document.createElement("option");
        opcion.value = tienda.id;
        opcion.textContent = `#${tienda.id} · ${tienda.nombre} (${tienda.zona})`;
        selectTienda.appendChild(opcion);
      });
    } catch (error) {
      console.error("Cargar tiendas:", error);
      selectTienda.innerHTML =
        '<option value="">No se pudieron cargar las tiendas</option>';
    }
  };

  // ---------- Render del kanban ----------
  const crearKanban = (contenedor, estados, etiquetas, tipo) => {
    contenedor.innerHTML = "";
    estados.forEach((estado) => {
      const columna = document.createElement("div");
      columna.className = `columna ${tipo}`;
      columna.dataset.estado = estado;

      columna.innerHTML = `
        <div class="encabezado enc-${tipo}-${estado}">
          <span>${etiquetas[estado]}</span>
          <span class="contador" data-contador="0">0</span>
        </div>
        <div class="cuerpo"></div>
      `;
      contenedor.appendChild(columna);
    });
  };

  const renderPedidos = (pedidos) => {
    const kanban = document.getElementById("kanban-pedidos");
    if (kanban.dataset.inicializado !== "si") {
      crearKanban(kanban, FLUJO_PEDIDO, ETIQUETAS_PEDIDO, "pedido");
      kanban.dataset.inicializado = "si";
    }

    kanban.querySelectorAll(".cuerpo").forEach((cuerpo) => (cuerpo.innerHTML = ""));
    kanban.querySelectorAll(".contador").forEach((contador) => (contador.textContent = "0"));

    pedidos.forEach((pedido) => {
      const cuerpoColumna = kanban.querySelector(
        `.columna[data-estado="${pedido.estado}"] .cuerpo`
      );
      if (!cuerpoColumna) return;

      const tarjeta = document.createElement("div");
      tarjeta.className = "tarjeta-orden";

      const productos = (pedido.items || [])
        .map(
          (item) =>
            `${item.nombre} (${[item.tamano, item.sabor]
              .filter(Boolean)
              .join(", ")}) x${item.cantidad}`
        )
        .join("<br />");

      const cliente = pedido.cliente ? pedido.cliente.nombre : "—";
      const celular = pedido.cliente ? pedido.cliente.celular : "";

      const siguiente = estadoSiguiente(pedido.estado, FLUJO_PEDIDO);

      tarjeta.innerHTML = `
        <div class="badge ${pedido.estado}">${ETIQUETAS_PEDIDO[pedido.estado]}</div>
        <div class="nro">Pedido #${pedido.id}</div>
        <div class="cliente">${cliente} ${celular ? `· ${celular}` : ""}</div>
        <div class="detalle">${productos}</div>
        <div class="detalle">Recojo: ${pedido.fecha_entrega || "Por coordinar"}</div>
        <div class="detalle">Pago: ${pedido.metodo_pago}</div>
        ${pedido.mensaje ? `<div class="detalle">Mensaje: "${pedido.mensaje}"</div>` : ""}
        <div class="fila"><span>Total</span><span>S/ ${Number(pedido.total).toFixed(2)}</span></div>
        <div class="acciones">
          ${
            siguiente
              ? `<button class="btn-avanzar" data-pedido="${pedido.id}" data-estado="${siguiente}">→ ${ETIQUETAS_PEDIDO[siguiente]}</button>`
              : ""
          }
          <button class="btn-cancelar" data-pedido="${pedido.id}" data-estado="cancelado">Cancelar</button>
        </div>
      `;

      cuerpoColumna.appendChild(tarjeta);
      const contador = cuerpoColumna.parentElement.querySelector(".contador");
      contador.textContent = Number(contador.textContent) + 1;
    });

    actualizarStats();
  };

  const renderReservas = (reservas) => {
    const kanban = document.getElementById("kanban-reservas");
    if (kanban.dataset.inicializado !== "si") {
      crearKanban(kanban, FLUJO_RESERVA, ETIQUETAS_RESERVA, "reserva");
      kanban.dataset.inicializado = "si";
    }

    kanban.querySelectorAll(".cuerpo").forEach((cuerpo) => (cuerpo.innerHTML = ""));
    kanban.querySelectorAll(".contador").forEach((contador) => (contador.textContent = "0"));

    reservas.forEach((reserva) => {
      const cuerpoColumna = kanban.querySelector(
        `.columna[data-estado="${reserva.estado}"] .cuerpo`
      );
      if (!cuerpoColumna) return;

      const tarjeta = document.createElement("div");
      tarjeta.className = "tarjeta-orden";

      const siguiente = estadoSiguiente(reserva.estado, FLUJO_RESERVA);

      tarjeta.innerHTML = `
        <div class="badge ${reserva.estado}">${ETIQUETAS_RESERVA[reserva.estado]}</div>
        <div class="nro">Reserva #${reserva.id}</div>
        <div class="cliente">${reserva.cliente.nombre} · ${reserva.cliente.celular}</div>
        <div class="detalle">${reserva.cantidad} x ${reserva.producto}</div>
        <div class="detalle">Compra: ${reserva.fecha_compra}</div>
        <div class="detalle">Recojo: ${reserva.fecha_recojo}</div>
        <div class="acciones">
          ${
            siguiente
              ? `<button class="btn-avanzar" data-reserva="${reserva.id}" data-estado="${siguiente}">→ ${ETIQUETAS_RESERVA[siguiente]}</button>`
              : ""
          }
          <button class="btn-cancelar" data-reserva="${reserva.id}" data-estado="cancelado">Cancelar</button>
        </div>
      `;

      cuerpoColumna.appendChild(tarjeta);
      const contador = cuerpoColumna.parentElement.querySelector(".contador");
      contador.textContent = Number(contador.textContent) + 1;
    });
  };

  // ---------- Actualización de estados (delegación de eventos) ----------
  document.addEventListener("click", async (event) => {
    const botonAvanzarPedido = event.target.closest(".btn-avanzar[data-pedido]");
    const botonCancelarPedido = event.target.closest(".btn-cancelar[data-pedido]");
    const botonAvanzarReserva = event.target.closest(".btn-avanzar[data-reserva]");
    const botonCancelarReserva = event.target.closest(".btn-cancelar[data-reserva]");

    const actualizarPedido = async (id, estado) => {
      try {
        ocultarError();
        const respuesta = await fetch(`${URL_PEDIDOS}/pedidos/${id}/estado`, {
          method: "PATCH",
          headers: cabeceras(),
          body: JSON.stringify({ estado }),
        });
        if (!respuesta.ok) {
          const data = await respuesta.json();
          throw new Error(data.error || "Error al actualizar pedido");
        }
        await recargarTodo();
      } catch (error) {
        console.error("Actualizar pedido:", error);
        mostrarError(error.message);
      }
    };

    const actualizarReserva = async (id, estado) => {
      try {
        ocultarError();
        const respuesta = await fetch(`${URL_RESERVAS}/reservas/${id}/estado`, {
          method: "PATCH",
          headers: cabeceras(),
          body: JSON.stringify({ estado }),
        });
        if (!respuesta.ok) {
          const data = await respuesta.json();
          throw new Error(data.error || "Error al actualizar reserva");
        }
        await recargarTodo();
      } catch (error) {
        console.error("Actualizar reserva:", error);
        mostrarError(error.message);
      }
    };

    if (botonAvanzarPedido) {
      await actualizarPedido(botonAvanzarPedido.dataset.pedido, botonAvanzarPedido.dataset.estado);
    } else if (botonCancelarPedido) {
      await actualizarPedido(botonCancelarPedido.dataset.pedido, botonCancelarPedido.dataset.estado);
    } else if (botonAvanzarReserva) {
      await actualizarReserva(botonAvanzarReserva.dataset.reserva, botonAvanzarReserva.dataset.estado);
    } else if (botonCancelarReserva) {
      await actualizarReserva(botonCancelarReserva.dataset.reserva, botonCancelarReserva.dataset.estado);
    }
  });

  // ---------- Carga de todo el tablero ----------
  const recargarTodo = async () => {
    const tiendaId = estadoLocal.tiendaId;
    if (!tiendaId) return;

    const [pedidos, reservas] = await Promise.all([
      fetch(`${URL_PEDIDOS}/pedidos?tienda_id=${tiendaId}`, {
        headers: cabeceras(),
      }).then((respuesta) => {
        if (!respuesta.ok) throw new Error("Error al cargar pedidos");
        return respuesta.json();
      }),
      fetch(`${URL_RESERVAS}/reservas?tienda_id=${tiendaId}`, {
        headers: cabeceras(),
      }).then((respuesta) => {
        if (!respuesta.ok) throw new Error("Error al cargar reservas");
        return respuesta.json();
      }),
    ]);

    // Registra los pedidos "nuevos" ya conocidos para el polling
    pedidos.forEach((pedido) => {
      if (pedido.estado === "nuevo" && !estadoLocal.pedidos.includes(pedido.id)) {
        estadoLocal.pedidos.push(pedido.id);
      }
    });

    renderPedidos(pedidos);
    renderReservas(reservas);
  };

  // ---------- Cambio de tienda ----------
  selectTienda.addEventListener("change", async () => {
    const tiendaId = Number(selectTienda.value);
    estadoLocal.tiendaId = tiendaId || null;
    estadoLocal.pedidos = [];
    estadoLocal.reservas = [];
    try {
      ocultarError();
      if (tiendaId) await recargarTodo();
    } catch (error) {
      console.error("Cargar tablero:", error);
      mostrarError(error.message);
    }
  });

  // ---------- Gestor de imágenes de productos (Cloudinary) ----------
  const selectProducto = document.getElementById("select-producto");
  const previewImagen = document.getElementById("preview-imagen");
  const inputImagen = document.getElementById("input-imagen");
  const btnSubir = document.getElementById("btn-subir");
  const btnQuitar = document.getElementById("btn-quitar");

  let productoSeleccionado = null;

  const cargarProductos = async () => {
    try {
      const tiendaId = estadoLocal.tiendaId || 1;
      const respuesta = await fetch(`${URL_PEDIDOS}/productos?tienda_id=${tiendaId}`, {
        headers: cabeceras(),
      });
      if (!respuesta.ok) throw new Error("Error al cargar productos");
      const productos = await respuesta.json();

      selectProducto.innerHTML =
        '<option value="">Selecciona un producto...</option>';
      productos.forEach((producto) => {
        const opcion = document.createElement("option");
        opcion.value = producto.id;
        opcion.textContent = `#${producto.id} · ${producto.nombre} (${producto.tipo})`;
        selectProducto.appendChild(opcion);
      });
    } catch (error) {
      console.error("Cargar productos:", error);
      selectProducto.innerHTML = '<option value="">No se pudieron cargar los productos</option>';
    }
  };

  const mostrarProducto = (producto) => {
    productoSeleccionado = producto || null;
    const tieneImagen = !!(producto && producto.imagen_url);
    previewImagen.innerHTML = tieneImagen
      ? `<img src="${producto.imagen_url}" alt="${producto.nombre}" />`
      : "Este producto aún no tiene imagen.";
    btnSubir.disabled = !inputImagen.files.length;
    btnQuitar.disabled = !tieneImagen;
  };

  selectProducto.addEventListener("change", async () => {
    const productoId = Number(selectProducto.value);
    if (!productoId) {
      mostrarProducto(null);
      return;
    }
    try {
      const respuesta = await fetch(`${URL_PEDIDOS}/productos?tienda_id=${estadoLocal.tiendaId || 1}`, {
        headers: cabeceras(),
      });
      const productos = await respuesta.json();
      const producto = productos.find((p) => p.id === productoId);
      mostrarProducto(producto || null);
    } catch (error) {
      console.error("Seleccionar producto:", error);
      mostrarError(error.message);
    }
  });

  inputImagen.addEventListener("change", () => {
    btnSubir.disabled = !inputImagen.files.length;
  });

  btnSubir.addEventListener("click", async () => {
    if (!productoSeleccionado || !inputImagen.files.length) return;
    try {
      ocultarError();
      btnSubir.disabled = true;
      const formData = new FormData();
      formData.append("imagen", inputImagen.files[0]);
      formData.append("producto_id", productoSeleccionado.id);
      formData.append("nombre", productoSeleccionado.nombre.toLowerCase().replace(/\s+/g, "-"));

      const respuesta = await fetch(`${URL_PEDIDOS}/imagenes`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await respuesta.json();
      if (!respuesta.ok) throw new Error(data.error || "Error al subir la imagen");

      inputImagen.value = "";
      mostrarProducto(data.producto);
      mostrarToast("Imagen actualizada", `${data.producto.nombre} con imagen nueva.`);
    } catch (error) {
      console.error("Subir imagen:", error);
      mostrarError(error.message);
    } finally {
      btnSubir.disabled = !inputImagen.files.length;
    }
  });

  btnQuitar.addEventListener("click", async () => {
    if (!productoSeleccionado) return;
    try {
      ocultarError();
      const respuesta = await fetch(`${URL_PEDIDOS}/productos/${productoSeleccionado.id}/imagen`, {
        method: "DELETE",
        headers: cabeceras(),
      });
      const data = await respuesta.json();
      if (!respuesta.ok) throw new Error(data.error || "Error al quitar la imagen");
      mostrarProducto(data.producto);
      mostrarToast("Imagen eliminada", `${data.producto.nombre}`);
    } catch (error) {
      console.error("Quitar imagen:", error);
      mostrarError(error.message);
    }
  });

  // ---------- Cerrar sesión ----------
  document.getElementById("btn-cerrar").addEventListener("click", () => {
    sessionStorage.removeItem("panel_token");
    sessionStorage.removeItem("panel_usuario");
    window.location.href = "login.html";
  });

  // ---------- Inicialización ----------
  cargarTiendas().then(async () => {
    const primera = selectTienda.querySelector("option");
    if (primera && primera.value) {
      selectTienda.value = primera.value;
      estadoLocal.tiendaId = Number(primera.value);
      await recargarTodo();
    }
    await cargarProductos();
  });

  // Polling de notificaciones de nuevos pedidos cada 12 segundos
  setInterval(verificarNuevosPedidos, 12000);
});