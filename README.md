# Plataforma Web — San Francisco de Asís

Panadería, pastelería y casa de tortas con 5 tiendas físicas en Huancayo (4 en el Centro y 1 en El Tambo, Perú).

Sistema construido con **arquitectura de microservicios** en Python/Flask:

- El **cliente** elige su tienda, personaliza tortas y bocaditos y registra su pedido.
- El **personal de tienda** recibe notificaciones en tiempo real y gestiona los pedidos en un tablero tipo **kanban**.
- Las tortas ya compradas en tienda física se pueden **separar/reservar** para recojo (microservicio 2).

---

## Arquitectura

```
Cliente (navegador)
        │
        ▼
  API GATEWAY (Flask, :5000) ── autenticación, enrutamiento, CORS
        │
   ┌────┴─────┐
   ▼          ▼
MICROSERVICIO 1          MICROSERVICIO 2
Recepción de Pedidos      Separado / Reserva de Tortas
(:5001)                   (:5002)
   │                        │
   ▼                        ▼
BD Pedidos              BD Inventario/Reservas
```

Cada microservicio es una aplicación Flask independiente, con su **propia base de datos SQLite** y su propio puerto. La comunicación se realiza vía REST/JSON. El gateway enruta:

| Ruta del gateway                  | Microservicio destino             |
| --------------------------------- | --------------------------------- |
| `/pedidos/api/tiendas`            | Microservicio 1 (catálogo)        |
| `/pedidos/api/tiendas/<id>/productos` | Microservicio 1 (productos)   |
| `/pedidos/api/pedidos`            | Microservicio 1 (crear/listar)    |
| `/pedidos/api/pedidos/<id>/estado`| Microservicio 1 (kanban)          |
| `/reservas/api/reservas`          | Microservicio 2 (separado)        |
| `/reservas/api/reservas/<id>/estado` | Microservicio 2 (kanban)       |

---

## Estructura de carpetas

```
san-francisco-de-asis/
├── gateway/                    # API Gateway (Flask, :5000)
├── microservicio-pedidos/      # Microservicio 1 (Flask, :5001)
├── microservicio-separado/     # Microservicio 2 (Flask, :5002)
├── frontend-cliente/           # Sitio web público del cliente (HTML/CSS/JS)
├── panel-tienda/               # Panel administrativo (login + dashboard kanban)
├── .env.example                # Variables de entorno de ejemplo
├── requirements.txt
├── docker-compose.yml          # Levanta gateway + 2 microservicios juntos
└── README.md
```

---

## Requisitos previos

- Python **3.11+**
- pip

## Instalación

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (opcional, hay valores por defecto)
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS
```

## Cómo levantar cada servicio

Cada servicio (gateway y microservicios) se ejecuta por separado en su propio puerto, **desde su propia carpeta**:

```bash
# Terminal 1 — Microservicio 1 (Pedidos) :5001
cd microservicio-pedidos
python app.py

# Terminal 2 — Microservicio 2 (Separado de tortas) :5002
cd microservicio-separado
python app.py

# Terminal 3 — API Gateway :5000
cd gateway
python app.py
```

Al primer arranque, cada microservicio crea su base de datos en `database/` y siembra los datos iniciales (las 5 tiendas, el catálogo de tortas/bocaditos y el inventario).

> **Nota:** todos los servicios deben levantar por igual. Si usas un solo proyecto, abre 3 terminales o usa Docker (ver abajo).

## Frontend de cliente

Puedes abrir el HTML directamente o servirlo con un servidor estático simple:

```bash
# Opción recomendada
python -m http.server 8080 --directory frontend-cliente
```

Luego visita las pantallas:

1. **`http://localhost:8080/index.html`** — Selección de tienda (5 sucursales).
2. **`http://localhost:8080/catalogo.html`** — Catálogo y personalización (tamaño, sabor, cantidad).
3. **`http://localhost:8080/checkout.html`** — Datos del cliente, resumen y confirmación.

El frontend consume el API Gateway en `http://localhost:5000` (definido en `frontend-cliente/static/js/config.js`, `API_BASE`).

## Panel de tienda (personal)

```bash
python -m http.server 8081 --directory panel-tienda
```

- **`http://localhost:8081/login.html`** — Acceso del personal.
- **`http://localhost:8081/dashboard.html`** — Tablero kanban de pedidos y de separado de tortas, con notificaciones de nuevos pedidos (polling cada 12 s, preparado para migrar a WebSockets/SSE).

**Credenciales por defecto** (definidas en el gateway vía `.env`):

| Usuario | Contraseña          |
| ------- | ------------------- |
| admin   | `san-francisco-2024`|

---

## Endpoints principales

### Microservicio 1 — Pedidos
| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| GET | `/api/tiendas` | Lista las 5 tiendas |
| GET | `/api/tiendas/<id>/productos` | Catálogo por tienda (`?tipo=torta|bocadito`) |
| POST | `/api/pedidos` | Crea un pedido y notifica a la tienda |
| GET | `/api/pedidos?tienda_id=` | Lista pedidos por tienda (`&estado=`) |
| PATCH | `/api/pedidos/<id>/estado` | Cambia el estado del pedido |

### Microservicio 2 — Separado de tortas
| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| POST | `/api/reservas` | Registra una torta comprada en tienda para separar |
| GET | `/api/reservas?tienda_id=` | Lista reservas por tienda |
| PATCH | `/api/reservas/<id>/estado` | Cambia el estado de la reserva |
| GET | `/api/inventario?tienda_id=` | Stock disponible para separar |

### Gateway
| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| POST | `/api/auth/login` | Devuelve el token del panel (usuario/contraseña) |
| GET/POST | `/pedidos/*` | Proxy hacia Microservicio 1 |
| GET/POST/PATCH | `/reservas/*` | Proxy hacia Microservicio 2 |

Las rutas de **lectura/gestión del panel** requieren el header:
```
Authorization: Bearer <token>
```
Las rutas públicas del cliente (`GET /pedidos/api/tiendas...`, `POST /pedidos/api/pedidos`) no requieren token.

---

## Notificaciones

El servicio `services/notificaciones.py` de cada microservicio expone `enviar_notificacion()`, que en desarrollo escribe la notificación en consola y en `database/logs/notificaciones.log`. Para integrar WhatsApp Business API, Twilio o SMTP (Flask-Mail), solo hay que reemplazar el cuerpo de esa función; el resto del sistema no requiere cambios.

---

## Ejecutar con Docker (opcional)

```bash
docker compose up --build
```

Levanta el gateway (:5000) y los dos microservicios (:5001, :5002). Los archivos de base de datos se montan en los volúmenes `database/` correspondientes.

---

## Buenas prácticas implementadas

- Microservicios independientes: **no comparten base de datos**.
- Variables de entorno mediante `python-dotenv` (`.env`).
- Errores en formato JSON (`{"error": "mensaje"}`) con códigos HTTP correctos.
- Código comentado en español y con estilo PEP 8.
- Estructura lista para Git (`.gitignore` + `.dockerignore`).

## Stack

- Flask 3, Flask-SQLAlchemy 3, Flask-CORS, Flask-Mail, python-dotenv, marshmallow, requests, gunicorn.
- SQLite en desarrollo (migrable a PostgreSQL).
- Frontend HTML5/CSS3/JS vanilla (Fetch API), Paleta de marca: marrón, naranja, naranja claro, turquesa y crema, tipografía Poppins, mobile-first.