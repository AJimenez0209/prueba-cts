# Prueba Técnica – CTS Turismo · Sorteo San Valentín

Aplicación Full Stack para gestionar un sorteo de San Valentín.

- **Backend:** Django + Django REST Framework (DRF)  
- **Frontend:** Nuxt 3 + Tailwind v4 + Pinia  
- **Tareas asíncronas:** Celery + Redis  
- **Infraestructura:** Dockerfiles individuales (backend/frontend) + Docker Compose  
- **Estado actual:** Flujo completo de registro, verificación, set de contraseña, envío de emails asíncronos, panel admin con lista de participantes (todos) y sorteo con notificación.

---

## Índice
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Flujo funcional](#flujo-funcional)
- [Endpoints (API) + cURL](#endpoints-api--curl)
- [Frontend (Nuxt 3)](#frontend-nuxt-3)
- [Docker](#docker)
- [Tests](#tests)
- [Checklist de calidad](#checklist-de-calidad)
- [Próximos pasos](#próximos-pasos)
- [Licencia](#licencia)

---

## Requisitos
- **Python** 3.11+ (probado en 3.12)  
- **Node.js** 18+  
- **Redis** (dev: Docker recomendado)  
- **Docker / Docker Compose** (para levantar el stack completo)

---

## Instalación y ejecución

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell

pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Variables de entorno

### Backend `.env`
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=*
FRONTEND_URL=http://localhost:3000

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@ctsturismo.local

USE_CELERY=1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

ADMIN_API_KEY=your-admin-api-key-here
```

### Frontend `.env`
```env
NUXT_PUBLIC_API_BASE_URL=http://backend:8000/api
NUXT_PUBLIC_ADMIN_API_KEY=your-admin-api-key-here
```

---

## Estructura del proyecto
```
prueba-cts/
├─ backend/
│  ├─ core/           # settings, celery, urls
│  ├─ participants/   # modelos, serializers, views, urls
│  ├─ tests/          # unit tests (serializers, views)
│  ├─ Dockerfile
│  └─ manage.py
├─ frontend/
│  ├─ pages/          # Nuxt pages: index, verify, admin/*
│  ├─ components/     # UI: AppCard, AppInput, AppButton, NavBar
│  ├─ composables/    # useApi
│  ├─ Dockerfile
│  └─ nuxt.config.ts
└─ docker-compose.yml
```

---

## Flujo funcional
1. **Registro (Home)**  
   - Usuario ingresa datos (nombre, email, teléfono).  
   - Backend responde con mensaje:  
     `¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.`  

2. **Verificación de correo**  
   - Usuario recibe email con enlace `/verify?token=...`.  
   - Backend valida token y responde con `participant_id`.  

3. **Set de contraseña**  
   - Usuario define contraseña en la vista `/verify`.  
   - Mensaje final:  
     `Tu cuenta ha sido activada. Ya estás participando en el sorteo.`  

4. **Panel Admin**  
   - Login con API Key.  
   - Lista de participantes (verificados y no verificados).  
   - Sorteo con notificación asíncrona vía Celery.  

---

## Endpoints (API) + cURL
### Público
- **POST** `/api/participants/register/`
- **GET** `/api/participants/verify/<token>/`
- **POST** `/api/participants/set-password/<participant_id>/`

### Admin (requiere header `X-API-Key`)
- **GET** `/api/admin/participants/`
- **POST** `/api/admin/draw/`

---

## Frontend (Nuxt 3)
- `/` → Home con inscripción y verificación por token  
- `/verify` → Verificación de correo y set de contraseña  
- `/admin/login` → Ingreso de API Key  
- `/admin/participants` → Lista de todos los participantes  
- `/admin/draw` → Sorteo  

---

## Docker
### Archivos incluidos
- `backend/Dockerfile` → Backend (Django + DRF + Celery worker).  
- `frontend/Dockerfile` → Frontend (Nuxt 3 + Tailwind).  
- `docker-compose.yml` → Orquesta los servicios:
  - **redis** (cola de Celery)  
  - **backend** (Django + API REST)  
  - **worker** (Celery)  
  - **frontend** (Nuxt 3, puerto 3000)  

### Levantar el stack
```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000/api  
- Redis: localhost:6379  

---

## Tests
### Backend
- Serializers y views cubiertos en `backend/tests/`  
- Ejecutar:
```bash
pytest
```

### Frontend
- Vitest + Vue Test Utils en `frontend/tests/`  
- Ejecutar:
```bash
npm run test
```

---

## Checklist de calidad
- [x] Registro con validación de duplicado  
- [x] Verificación de correo por token  
- [x] Set de contraseña  
- [x] Emails asíncronos (Celery + Redis)  
- [x] Admin API: lista + sorteo  
- [x] Frontend con 5 vistas  
- [x] Tailwind v4 integrado  
- [x] Admin protegido (UI + middleware)  
- [x] Tests de backend y frontend  
- [x] Dockerfiles y docker-compose  
- [ ] Deploy en producción  

---

## Próximos pasos


---

## Licencia
Uso interno para evaluación técnica.
