# Prueba Técnica – CTS Turismo · Sorteo San Valentín

Aplicación Full Stack para gestionar un sorteo de San Valentín.
- **Backend:** Django + Django REST Framework (DRF)
- **Tareas asíncronas:** Celery + Redis
- **Estado actual:** Registro, verificación por correo, set de contraseña, envío de emails asíncrono, Admin API (listado y sorteo con notificación).

## Índice
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Endpoints (API) + cURL](#endpoints-api--curl)
  - [Flujo público](#flujo-público)
  - [Admin API](#admin-api)
  - [Debug opcional](#debug-opcional)
- [Celery + Redis (emails asíncronos)](#celery--redis-emails-asíncronos)
- [Decisiones técnicas](#decisiones-técnicas)
- [Manejo de errores](#manejo-de-errores)
- [Checklist de calidad](#checklist-de-calidad)
- [Próximos pasos](#próximos-pasos)
- [Licencia](#licencia)

---

## Requisitos
- **Python** 3.11+ (probado en 3.12)
- **Pip** / **venv**
- **Redis** (dev: Docker recomendado)
- (Próximamente) **Node 18+** para frontend

---

## Instalación y ejecución

> Comandos para **Windows (PowerShell)**; en macOS/Linux cambia rutas y activación de venv.

```powershell
cd path\to\your\workspace
git clone https://github.com/<tu-usuario>/prueba-cts.git
cd prueba-cts\backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1   # (Windows)
# source .venv/bin/activate      # (macOS / Linux)

pip install -r requirements.txt
```

### Variables de entorno
Crea `backend/.env` a partir de este ejemplo:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=*
FRONTEND_URL=http://localhost:3002

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@ctsturismo.local

# Celery + Redis (async)
USE_CELERY=1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Admin API (Header X-API-Key)
ADMIN_API_KEY=your-admin-api-key-here
```

> **Generar SECRET y API KEY**
> - `DJANGO_SECRET_KEY`: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
> - `ADMIN_API_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Migraciones y servidor
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
- Dev server: `http://127.0.0.1:8000/`
- Admin Django: `http://127.0.0.1:8000/admin`

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta Django | — |
| `DEBUG` | Modo debug (1/0) | `1` |
| `ALLOWED_HOSTS` | Hosts permitidos | `*` |
| `FRONTEND_URL` | Base para armar link de verificación | `http://localhost:3002` |
| `EMAIL_BACKEND` | Backend de email (dev: consola) | `django.core.mail.backends.console.EmailBackend` |
| `DEFAULT_FROM_EMAIL` | Remitente por defecto | `no-reply@ctsturismo.local` |
| `USE_CELERY` | Encolar tareas (1) o sync (0) | `1` |
| `CELERY_BROKER_URL` | Broker Celery (Redis) | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Result backend (Redis) | `redis://localhost:6379/0` |
| `ADMIN_API_KEY` | Clave para Admin API (header) | — |

---

## Estructura del proyecto

```
prueba-cts/
└─ backend/
   ├─ manage.py
   ├─ requirements.txt
   ├─ .env.example (sugerido para el repo)
   ├─ .env          (no subir a git)
   ├─ core/
   │  ├─ settings.py        # apps, DB, CORS, email, Celery, API key
   │  ├─ urls.py            # monta /api/
   │  ├─ wsgi.py / asgi.py
   │  └─ celery.py + __init__.py (exponen celery_app)
   └─ participants/
      ├─ models.py          # Participant
      ├─ serializers.py     # ParticipantCreateSerializer, ParticipantSerializer
      ├─ views.py           # register, verify, set-password, admin_* y debug opcional
      ├─ urls.py            # rutas de la app
      └─ tasks.py           # send_verification_email_task, send_winner_email_task, ping_task (debug)
```

**Convenciones**
- En URLs: **guion** (`set-password`) por legibilidad.
- En Python: **guion bajo** (`set_password`) por sintaxis.

---

## Endpoints (API) + cURL

### Flujo público

#### 1) Registro de participante
**POST** `/api/participants/register/`

Body:
```json
{
  "full_name": "Ana Pérez",
  "email": "ana@example.com",
  "phone": "+56 9 1234 5678"
}
```

cURL:
```bash
curl -X POST http://127.0.0.1:8000/api/participants/register/   -H "Content-Type: application/json"   -d '{"full_name":"Ana Pérez","email":"ana@example.com","phone":"+56 9 1234 5678"}'
```
Respuesta (201):
```json
{
  "message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.",
  "async": true,
  "task_id": "<id-de-la-tarea-si-USE_CELERY=1>"
}
```

> El correo se imprime en **la consola del worker** (EMAIL_BACKEND=consola).

#### 2) Verificación de correo
**GET** `/api/participants/verify/<token>/`

cURL:
```bash
curl -X GET http://127.0.0.1:8000/api/participants/verify/550e8400-e29b-41d4-a716-446655440000/
```
Respuesta (200):
```json
{"detail":"Correo verificado correctamente","participant_id":1}
```

#### 3) Set de contraseña
**POST** `/api/participants/set-password/<participant_id>/`

Body:
```json
{"password":"Prueba1234"}
```
cURL:
```bash
curl -X POST http://127.0.0.1:8000/api/participants/set-password/1/   -H "Content-Type: application/json"   -d '{"password":"Prueba1234"}'
```
Respuesta (200):
```json
{"detail":"Tu cuenta ha sido activada. Ya estás participando en el sorteo."}
```

---

### Admin API

> Requiere header `X-API-Key: <valor de ADMIN_API_KEY>`

#### Listar participantes
**GET** `/api/admin/participants/?verified=1&page=1&page_size=20&search=ana`

cURL:
```bash
curl -X GET "http://127.0.0.1:8000/api/admin/participants/?verified=1&page=1&page_size=20&search=ana"   -H "X-API-Key: your-admin-api-key-here"
```

Respuesta (200):
```json
{
  "page": 1,
  "page_size": 20,
  "total": 3,
  "total_pages": 1,
  "results": [
    {"id":5,"full_name":"Ana Pérez","email":"ana5@example.com","phone":"+56 9 1234 5678","is_verified":true,"created_at":"2025-09-22T21:59:46Z"}
  ]
}
```

#### Sorteo de ganador (notifica por email async)
**POST** `/api/admin/draw/`

cURL:
```bash
curl -X POST "http://127.0.0.1:8000/api/admin/draw/"   -H "X-API-Key: your-admin-api-key-here"
```
Respuesta (200):
```json
{
  "winner": {
    "id": 5,
    "full_name": "Ana Pérez",
    "email": "ana5@example.com",
    "phone": "+56 9 1234 5678",
    "is_verified": true,
    "created_at": "2025-09-22T21:59:46Z"
  },
  "detail": "Ganador seleccionado y notificado por correo (tarea Celery encolada).",
  "task_id": "<id-de-la-tarea-celery>"
}
```

---

### Debug (opcional)

**GET** `/api/debug/celery/` → `{"USE_CELERY": true}`  
**POST** `/api/debug/ping-task/` → `{"task_id": "..."}` (worker debe mostrar `Received task...`).

---

## Celery + Redis (emails asíncronos)

### Opción rápida con Docker (Redis)
```powershell
docker run -d --name redis -p 6379:6379 redis:7
```

### Worker Celery (Windows usa -P solo)
```powershell
# en carpeta backend/ con venv activo
celery -A core worker -l info -P solo
# o
.\.venv\Scripts\python.exe -m celery -A core worker -l info -P solo
```

**Qué deberías ver** en el worker al registrar/ sortear:
```
[INFO/MainProcess] Task participants.tasks.send_verification_email_task[...] received
[INFO/MainProcess] Task ... succeeded ...
```
El **correo** se imprime en la **consola del worker** (no del server).

> Si `USE_CELERY=0`, la vista ejecuta el envío en modo **síncrono** (verás el correo en la consola del **server**).

---

## Decisiones técnicas
- **DRF** para serialización/validación y diseño claro de endpoints.
- **Email de verificación** y **notificación a ganador** como **tasks Celery** (requisito asíncrono).
- **Selección aleatoria** del ganador sin `order_by('?')` (evita penalización por full-scan).
- **Admin API con API Key** por simplicidad de pruebas (en producción → auth/permissions).
- **Convenciones de rutas** y separación `core/` vs `participants/` para escalar.

---

## Manejo de errores
- Email duplicado → **400** con detalle del campo.
- Token inválido en verificación → **404**.
- Set password sin verificación previa → **403**.
- Password débil (<8) → **400**.
- Admin API sin API Key o inválida → **401**.
- Admin API sin configurar `ADMIN_API_KEY` → **500** con mensaje claro.

---

## Checklist de calidad
- [x] Registro con validación de duplicado
- [x] Verificación de correo por token
- [x] Set de contraseña (hash seguro)
- [x] Emails asíncronos (Celery + Redis)
- [x] Admin API: listar + sorteo con email al ganador
- [x] cURL listo para Postman
- [ ] Frontend (5 vistas mínimas)
- [ ] Tests (serializers, views)
- [ ] Docker Compose (web+redis+worker)
- [ ] Despliegue (ASGI/WSGI production-ready)

---

## Próximos pasos
- **Frontend** (form de inscripción, verificación+password, panel admin con sorteo).
- **Tests** de unidad e integración.
- **Docker Compose** para levantar stack completo fácilmente.
- **Mejoras**: máscara de email en Admin API, rate limiting, logging estructurado.

---

## Licencia
Uso interno para evaluación técnica.
