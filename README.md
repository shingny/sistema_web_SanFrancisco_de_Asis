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
| GET | `/api/productos` | Lista productos para el panel (`?tienda_id=&tipo=`) |
| POST | `/api/imagenes` | Sube una imagen a Cloudinary (multipart; requiere token) |
| PATCH/DELETE | `/api/productos/<id>/imagen` | Actualiza/elimina la imagen de un producto (requiere token) |
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

## Desplegar en Render (cloud)

El proyecto incluye un blueprint `render.yaml` que crea **3 Web Services** y **2 Sitios Estáticos**:

| Servicio | Tipo | Carpeta |
| -------- | ---- | ------- |
| `sfa-gateway` | Web Service (Flask) | `gateway/` |
| `sfa-pedidos` | Web Service (Flask) | `microservicio-pedidos/` |
| `sfa-separado` | Web Service (Flask) | `microservicio-separado/` |
| `sfa-frontend` | Static Site | `frontend-cliente/` |
| `sfa-panel` | Static Site | `panel-tienda/` |

### Pasos

1. **Configura la URL del gateway** (2 archivos):
   - `frontend-cliente/static/js/config.js` → `API_BASE` con tu URL de gateway (`https://sfa-gateway.onrender.com`).
   - `panel-tienda/static/js/config.js` → lo mismo.
2. **Haz push** del `render.yaml` a GitHub.
3. En Render: **New → Blueprint** → elige el repositorio → **Apply**. Render crea y despliega los 5 servicios automáticamente.
4. Si cambias los nombres de los servicios, actualiza en `render.yaml`:
   - `PEDIDOS_URL` y `SEPARADO_URL` del gateway.
   - `API_BASE` de los frontends.

### Consideraciones importantes de Render

- **Puerto:** cada microservicio ya escucha en la variable `PORT` que inyecta Render (con `gunicorn app:app`).
- **SQLite es efímero:** en el plan free de Render el disco se reinicia al redeploy y los pedidos/reservas se pierden. Por eso este proyecto usa **PostgreSQL** cuyas bases viven en **Alwaysdata** (ver "Bases de datos en Alwaysdata"). En `render.yaml` está la variable `DATABASE_URL` (con `sync: false`) para que la completes en el panel de Render apuntando a tu base de Alwaysdata.
- **Cloudinary:** configura `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` y `CLOUDINARY_API_SECRET` en el servicio `sfa-pedidos` (en `render.yaml` están con `sync: false` para que las completes al aplicar el blueprint).
- **Sleep del plan free:** los servicios de plan free se duermen tras ~15 min sin uso; la primera visita tarda unos segundos en "despertarlos".
- **CORS:** el gateway permite todos los orígenes, así que los Static Sites pueden consumir la API sin problemas.

---

## Desplegar con Alwaysdata (bases de datos en la nube)

En esta arquitectura **las aplicaciones se despliegan en Render** y **las bases de datos (PostgreSQL) se alojan en Alwaysdata**, cada microservicio con la suya. También puedes desplegar las aplicaciones íntegramente en Alwaysdata si lo prefieres (ver más abajo).

### Bases de datos en Alwaysdata (PostgreSQL)

1. En tu panel de **Alwaysdata** (https://admin.alwaysdata.com) crea **2 bases de datos PostgreSQL**:
   - `nombre_bd_pedidos` → para el Microservicio 1.
   - `nombre_bd_reservas` → para el Microservicio 2.

   Cada microservicio debe tener **su propia base** (no se comparten).

2. Alwaysdata te da una cadena de conexión similar a:
   ```
   postgresql://usuario:clave@db.alwaysdata.net:5432/nombre_bd_pedidos
   ```
   En Alwaysdata puedes habilitar el acceso externo (Remote SQL) para que Render pueda conectar.

3. En **Render**, en el servicio `sfa-pedidos` define `DATABASE_URL` con la URL de `nombre_bd_pedidos`; en `sfa-separado` define `DATABASE_URL` con la URL de `nombre_bd_reservas`.

4. Al arrancar, cada microservicio crea sus tablas y siembra los datos iniciales automáticamente (`create_all`).

> **Nota:** el proyecto también soporta **MariaDB/MySQL** si prefieres — cambiarías la URL de conexión y añadirías `pymysql` a `requirements.txt`; el código no cambia.

### (Alternativa) Desplegar todas las apps en Alwaysdata

Alwaysdata ejecuta Python vía **WSGI (Phusion Passenger)**, no con `python app.py`. El repo ya incluye `passenger_wsgi.py` en cada microservicio.

| Sitio | Tipo | Application path / carpeta | Entry point | URL sugerida |
| ----- | ---- | -------------------------- | ----------- | ------------ |
| `sfa-pedidos` | Python | `microservicio-pedidos/` | `passenger_wsgi.py` | `sfa-pedidos.tu-usuario.alwaysdata.net` |
| `sfa-separado` | Python | `microservicio-separado/` | `passenger_wsgi.py` | `sfa-separado.tu-usuario.alwaysdata.net` |
| `sfa-gateway` | Python | `gateway/` | `passenger_wsgi.py` | `sfa-gateway.tu-usuario.alwaysdata.net` |
| `sfa-frontend` | Static | `frontend-cliente/` | — | `sfa-frontend.tu-usuario.alwaysdata.net` |
| `sfa-panel` | Static | `panel-tienda/` | — | `sfa-panel.tu-usuario.alwaysdata.net` |

Pasos (solo si eliges esta alternativa):

1. **Sube el código** al servidor (git clone, FTP o el "git deploy" de Alwaysdata).
2. **Instala las dependencias** desde la carpeta del repo:
   ```bash
   mkdir -p ~/venvs && python3 -m venv ~/venvs/sfa && ~/venvs/sfa/bin/pip install -r requirements.txt
   ```
   Y configura ese entorno como "Python interpreter" de tus sitios Python (en Alwaysdata: Sites → tu sitio → Configuration).
3. **Crea los 5 sitios** del cuadro anterior.
4. **Variables de entorno** del gateway (en Alwaysdata: Sites → sfa-gateway → Environment variables):
   - `PEDIDOS_URL=https://sfa-pedidos.tu-usuario.alwaysdata.net`
   - `SEPARADO_URL=https://sfa-separado.tu-usuario.alwaysdata.net`
   - (opcional) `PANEL_USER`, `PANEL_PASSWORD`, `PANEL_TOKEN`.
   - En cada microservicio, su `DATABASE_URL` (PostgreSQL local de Alwaysdata) y, en pedidos, las credenciales de Cloudinary.
   > Las variables del panel de Alwaysdata tienen prioridad sobre el `.env`.
5. **Configura `API_BASE`** en `frontend-cliente/static/js/config.js` y `panel-tienda/static/js/config.js` con `https://sfa-gateway.tu-usuario.alwaysdata.net`.

---

## Buenas prácticas implementadas

- Microservicios independientes: **no comparten base de datos**.
- Variables de entorno mediante `python-dotenv` (`.env`).
- Errores en formato JSON (`{"error": "mensaje"}`) con códigos HTTP correctos.
- Código comentado en español y con estilo PEP 8.
- Estructura lista para Git (`.gitignore` + `.dockerignore`).

## Stack

- Flask 3, Flask-SQLAlchemy 3, Flask-CORS, Flask-Mail, python-dotenv, marshmallow, requests, gunicorn.
- **Cloudinary** (imágenes de productos).
- SQLite en desarrollo; **PostgreSQL en producción** (bases en Alwaysdata).
- Frontend HTML5/CSS3/JS vanilla (Fetch API), Paleta de marca: marrón, naranja, naranja claro, turquesa y crema, tipografía Poppins, mobile-first.

---

## Imágenes con Cloudinary

Las imágenes de los productos se guardan en **Cloudinary**. Cada producto tiene los campos:

- `imagen_url`: URL pública de la imagen (la que consume el frontend).
- `public_id`: identificador de la imagen en Cloudinary (para poder reemplazarla o eliminarla).

### Configuración (variables de entorno)

En tu **Cloudinary Dashboard** obtén el cloud name, API key y API secret y expón:

```
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

(Opcional) `CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name`.

Estas variables solo son necesarias en el **microservicio 1 (pedidos)**, que es quien gestiona los productos.

### Cómo se usan

- El **cliente** (`catalogo.html`) muestra `producto.imagen_url`. Si un producto aún no tiene imagen, la tarjeta muestra su color de marca.
- El **panel de tienda** (`dashboard.html` → sección "Catálogo · Imágenes") permite:

  1. Seleccionar un producto de la tienda.
  2. Ver la imagen actual.
  3. **Subir una imagen** (`POST /pedidos/api/imagenes`, multipart) que se carga a Cloudinary y se asocia al producto.
  4. **Quitar la imagen** (`DELETE /pedidos/api/productos/<id>/imagen`).

Ambas operaciones requieren token del panel (Bearer).

---