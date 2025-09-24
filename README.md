# Prueba Técnica – CTS Turismo · Sorteo San Valentín

Aplicación **Full Stack** para gestionar un sorteo de San Valentín.  
Incluye **backend en Django/DRF + Celery/Redis** y **frontend en Nuxt 3 (Vue 3 + Pinia)**.

- **Backend:** Django + Django REST Framework (DRF)  
- **Tareas asíncronas:** Celery + Redis  
- **Frontend:** Nuxt 3 (Vue 3 Composition API, Pinia, Tailwind minimal)  
- **Estado actual:** Flujo completo funcionando:
  - Registro
  - Verificación por correo
  - Set de contraseña
  - Envío de emails asíncrono
  - Panel admin: login, lista de participantes, sorteo con notificación

---

## Índice
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Celery + Redis](#celery--redis)
- [Variables de entorno](#variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Endpoints (API) + cURL](#endpoints-api--curl)
- [Flujo completo](#flujo-completo)
- [Decisiones técnicas](#decisiones-técnicas)
- [Manejo de errores](#manejo-de-errores)
- [Checklist de calidad](#checklist-de-calidad)
- [Próximos pasos](#próximos-pasos)
- [Licencia](#licencia)

---

## Requisitos
- **Python 3.11+**  
- **pip / venv**  
- **Redis** (Docker recomendado)  
- **Node.js 18+** para frontend  

---

## Instalación y ejecución

### Backend
```bash
cd prueba-cts/backend
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
cp .env.example .env
# edita .env con tu SECRET_KEY y ADMIN_API_KEY
python manage.py migrate
python manage.py runserver 8000
```
Dev server: http://127.0.0.1:8000/

### Frontend
```bash
cd prueba-cts/frontend
npm install
cp .env.example .env
# edita .env con la URL del backend (ej. http://127.0.0.1:8000/api)
npm run dev
```
Frontend: http://localhost:3000/

### Celery + Redis
Levanta Redis (Docker recomendado):
```bash
docker run -d --name redis -p 6379:6379 redis:7
```

Worker Celery:
```bash
cd backend
celery -A core worker -l info -P solo
```

---

## Variables de entorno

### Backend (`backend/.env`)
```env
DJANGO_SECRET_KEY=your-secret
DEBUG=1
ALLOWED_HOSTS=*
FRONTEND_URL=http://localhost:3000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@ctsturismo.local
USE_CELERY=1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
ADMIN_API_KEY=your-admin-api-key-here
```

### Frontend (`frontend/.env`)
```env
NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
NUXT_PUBLIC_ADMIN_API_KEY=
```

---

## Estructura del proyecto

```
prueba-cts/
├─ backend/
│  ├─ core/ (settings, celery, urls)
│  ├─ participants/ (models, serializers, views, tasks)
│  └─ manage.py
├─ frontend/
│  ├─ app.vue
│  ├─ pages/
│  │   ├─ index.vue           # Inscripción
│  │   ├─ verify.vue          # Verificación + set de contraseña
│  │   └─ admin/
│  │        ├─ login.vue      # Login admin
│  │        ├─ participants.vue  # Lista admin
│  │        └─ draw.vue       # Sorteo admin
│  ├─ stores/admin.ts
│  ├─ composables/useApi.ts
│  └─ middleware/require-admin.ts
└─ README.md
```

---

## Endpoints (API) + cURL

### Público
**1) Registro**  
POST `/api/participants/register/`
```bash
curl -X POST http://127.0.0.1:8000/api/participants/register/   -H "Content-Type: application/json"   -d '{"full_name":"Ana Pérez","email":"ana@example.com","phone":"+56 9 1234 5678"}'
```
Respuesta (201):
```json
{"message":"¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.","async":true,"task_id":"<id>"}
```

**2) Verificación**  
GET `/api/participants/verify/<token>/`

**3) Set de contraseña**  
POST `/api/participants/set-password/<participant_id>/`

---

### Admin (requiere `X-API-Key`)
**Listar participantes**  
GET `/api/admin/participants/?verified=1&page=1&page_size=20&search=ana`

**Sorteo**  
POST `/api/admin/draw/`
```json
{
  "winner": {"id":5,"full_name":"Ana Pérez","email":"ana@example.com", ...},
  "detail":"Ganador seleccionado y notificado por correo (tarea Celery encolada).",
  "task_id":"<id>"
}
```

---

## Flujo completo

1. **Inscripción (/):** formulario → banner “¡Gracias por registrarte!...”
2. **Verificación (/verify):** token → “Correo verificado correctamente” → set password.
3. **Set password:** mensaje final → “Tu cuenta ha sido activada. Ya estás participando en el sorteo.”
4. **Admin login (/admin/login):** ingresar API Key.
5. **Lista (/admin/participants):** tabla con búsqueda/paginación.
6. **Sorteo (/admin/draw):** botón → muestra ganador + confirma notificación.

---

## Decisiones técnicas
- **Nuxt 3** con `pages/` para simplicidad y rutas automáticas.
- **Pinia** para persistir `ADMIN_API_KEY` en localStorage.
- **useApi.ts** centraliza llamadas con `X-API-Key`.
- **Celery + Redis** garantizan envío de emails asíncrono.
- **Mensajes al usuario** replican literal el enunciado del PDF.

---

## Manejo de errores
- Registro duplicado → banner rojo “Este email ya está registrado”.
- Token inválido → mensaje de error en `/verify`.
- Password < 8 chars → validación visual + error backend.
- Admin API sin clave → redirección a login.

---

## Checklist de calidad
- [x] 5 vistas frontend (Inscripción, Verify+Password, Login, Lista, Sorteo)
- [x] Mensajes literales del PDF
- [x] Backend con DRF + Celery + Redis
- [x] API Key para admin
- [x] Manejo de estados: loading / error / success
- [ ] Tests básicos (opcional, plus)
- [ ] Docker Compose (opcional, plus)

---

## Próximos pasos
- Añadir **tests** de serializers y componentes Vue.
- Crear `docker-compose.yml` para levantar stack completo.
- Mejorar UI admin (navbar con logout, máscara de email).

---

## Licencia
Uso interno para evaluación técnica.
