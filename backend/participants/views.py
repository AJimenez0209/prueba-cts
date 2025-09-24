import random
from math import ceil
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from  core.settings import USE_CELERY
from .serializers import ParticipantCreateSerializer
from .models import Participant
from .tasks import send_verification_email_task
from .tasks import send_winner_email_task


from django.shortcuts import get_object_or_404

import logging

logger = logging.getLogger(__name__)


@api_view(["POST"])
def register(request):
    """
    Crea un participante si el email no existe y envía email de verificación.
    Respuestas:
    - 201: {"message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta."}
    - 400: errores de validación
    """
    s = ParticipantCreateSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    participant = s.save()

    # En esta parte (1) lo dejamos síncrono para que funcione sin Redis:
    if settings.USE_CELERY:
        # (lo activaremos en Parte 3)
        logger.info(
            "USANDO CELERY: encolando send_verification_email_task.delay(%s)",
            participant.id,
        )
        send_verification_email_task.delay(participant.id)
    else:
        # ejecución directa (síncrona) imprime por consola en dev
        logger.info(
            "SIN CELERY: ejecutando send_verification_email_task(%s) en línea",
            participant.id,
        )
        send_verification_email_task(participant.id)

    return Response(
        {
            "message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta."
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def verify_token(request, token):
    """
    Verifica el correo a partir del token enviado.
    """
    participant = get_object_or_404(Participant, verification_token=token)

    if participant.is_verified:
        return Response(
            {"detail": "Ya verificado", "participant_id": participant.id}, status=200
        )

    participant.is_verified = True
    participant.save(update_fields=["is_verified"])

    return Response(
        {"detail": "Correo verificado correctamente", "participant_id": participant.id},
        status=200,
    )


@api_view(["POST"])
def set_password(request, participant_id):
    """
    Crea la contraseña del participante ya verificado.
    """
    participant = get_object_or_404(Participant, id=participant_id)

    if not participant.is_verified:
        return Response({"detail": "Cuenta no verificada"}, status=403)

    password = request.data.get("password")
    if not password or len(password) < 8:
        return Response({"password": "Debe tener al menos 8 caracteres"}, status=400)

    participant.set_password(password)

    return Response(
        {"detail": "Tu cuenta ha sido activada. Ya estás participando en el sorteo."},
        status=200,
    )


@api_view(["GET"])
def debug_celery(request):
    return Response({"USE_CELERY": settings.USE_CELERY})


# Helper para autenticación simple con API Key en header, su función es devolver None si OK, o Response(...) si falla.


def _require_api_key(request):
    """
    Valida el header X-API-Key contra settings.ADMIN_API_KEY.
    Devuelve None si OK; Response(...) si falla.
    """
    configured = getattr(settings, "ADMIN_API_KEY", "") or ""
    sent = request.headers.get("X-API-Key") or request.META.get("HTTP_X_API_KEY")

    if not configured:
        # 500 porque el servidor no está configurado correctamente
        return Response(
            {"detail": "ADMIN_API_KEY no configurada en el servidor"}, status=500
        )

    if not sent or sent != configured:
        return Response({"detail": "No autorizado"}, status=401)

    return None


@api_view(["GET"])
def admin_participants(request):
    """
    Lista participantes para el panel admin.
    Query params:
      - verified: 1|0
      - search: texto (en full_name o email)
      - page: número (default 1)
      - page_size: número (default 20, max 100)
    """
    auth = _require_api_key(request)
    if auth:
        return auth

    qs = Participant.objects.all().order_by("-created_at")

    verified = request.GET.get("verified")
    if verified == "1":
        qs = qs.filter(is_verified=True)
    elif verified == "0":
        qs = qs.filter(is_verified=False)

    search = request.GET.get("search")
    if search:
        qs = qs.filter(
            models.Q(full_name__icontains=search) | models.Q(email__icontains=search)
        )

    try:
        page = int(request.GET.get("page", "1"))
        page_size = min(int(request.GET.get("page_size", "20")), 100)
    except ValueError:
        return Response({"detail": "Parámetros de paginación inválidos"}, status=400)

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]

    data = ParticipantCreateSerializer(items, many=True).data
    return Response(
        {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if page_size else 1,
            "results": data,
        },
        status=200,
    )


# escoge un ganador aleatorio entre los verificados y envía email (async con Celery)
@api_view(["POST"])
def admin_draw(request):
    """
    Sortea un ganador entre participantes verificados y envía correo (Celery).
    """
    auth = _require_api_key(request)
    if auth:
        return auth

    qs = Participant.objects.filter(is_verified=True)
    count = qs.count()
    if count == 0:
        return Response(
            {"detail": "No hay participantes verificados para el sorteo"}, status=400
        )

    # Selección aleatoria eficiente (evita order_by('?'))
    idx = random.randrange(count)
    winner = qs[idx]

    if settings.USE_CELERY:
        async_result = send_winner_email_task.delay(winner.id)
    else:
        send_winner_email_task(winner.id)
        async_result = type(
            "R", (), {"id": None}
        )()  # objeto simulado con id=None, guarda en async_result.id el valor None o id real

    data = {
        "winner": ParticipantCreateSerializer(winner).data,
        "detail": "Ganador seleccionado y notificado por correo (tarea Celery encolada).",
        "task_id": async_result.id,
    }

    return Response(
        data,
        status=200,
    )
