# AGENTS.md - RestauranteApp

## Structure
- `api/` Flask app (package). Entrypoint `api.create_app()` in `api/__init__.py`
- `api/Modelos/` SQLAlchemy 2.0 models with `Mapped`/`mapped_column`, `to_json`, `from_json`, `update_from_json`
- `api/Cruds/` CRUD views using `ItemAPI`/`GroupAPI` from `api/Cruds/crudGenerico.py` + `register_api()`
- `api/database.py` lazy engine/session via `init_db(app=None)`. Creates `instance/` dir for SQLite files. Enables FK pragmas.
- `frontend/` Vite + React 19 app (axios). Dev server proxies `/api` -> `http://127.0.0.1:5000` (stripped)

## Dev commands
**Backend (Flask)**
- Create venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install flask sqlalchemy flask-cors` (as needed)
- Run dev: `source .venv/bin/activate && flask --app api run --host 127.0.0.1 --port 5000`
- Init DB: `init_db(app)` called by `create_app()`; models imported in `api/database.py` to register metadata

**Frontend (Vite)**
- Install: `cd frontend && npm install`
- Dev: `cd frontend && npm run dev` (http://127.0.0.1:5173)
- Build: `cd frontend && npm run build`
- Lint: `cd frontend && npm run lint` (oxlint)

## API patterns
- Routes registered by `register_api(app, model, name, ...)` -> `/{name}/` (GET, POST) and `/{name}/<int:id>` (GET, PATCH, DELETE). Some use camelCase names (e.g. `unidadesMedida`, `ingresoMercaderia`, `recetasProductos`, `productoVenta`, `consumoPersonal`, `metodosPago`).
- `GroupAPI.get()` supports `?activo=true|false` only if model has `activo`.
- Errors go through `respuesta_error()` -> JSON with appropriate status codes.
- CORS enabled in `api.create_app()` via `flask-cors` (allow all origins for dev).

## Frontend patterns
- API client: `frontend/src/services/api.js` uses `baseURL: "http://127.0.0.1:5000"` with `Content-Type: application/json`
- Per-entity services in `frontend/src/services/*Service.js` (getAll/getById/create/update/remove)
- Hooks in `frontend/src/hooks/use*.js` with CRUD helpers; `useProducto` and `usePersonal` expose `toggleActivo(item)`
- Components: `components/{Entity}/{Entity}Nuevo.jsx`, `components/{Entity}/{Entity}Listar.jsx`. Listar has Editar/Eliminar; entities with `activo` have Activar/Desactivar
- Admin UI: `frontend/src/pages/AdminPanel.jsx` manages all entities via sidebar

## Gotchas
- SQLite needs `instance/` dir (created by `init_db`). FK enforced via PRAGMA on connect.
- In `api/database.py`, engine/session are lazy; `init_db(app)` configures them and imports `api.Modelos` to register tables.
- When adding models/CRUDs: create in `api/Modelos/`, add to `api/Modelos/__init__.py`, create CRUD in `api/Cruds/`, register in `api/__init__.py`. Add services/hooks/components/pages as needed.
- Vite proxy exists but frontend uses direct baseURL to Flask in current setup.
- `schema.md` is the source of truth for schema; update `memory.md` with summaries of schema changes.
