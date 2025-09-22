from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import ParticipantCreateSerializer
from .models import Participant
from .tasks import send_verification_email_task
from django.shortcuts import get_object_or_404


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
        send_verification_email_task.delay(participant.id)
    else:
        # ejecución directa (síncrona) imprime por consola en dev
        send_verification_email_task(participant.id)

    return Response(
        {"message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta."},
        status=status.HTTP_201_CREATED,
    )



@api_view(["GET"])
def verify_token(request, token):
    """
    Verifica el correo a partir del token enviado.
    """
    participant = get_object_or_404(Participant, verification_token=token)

    if participant.is_verified:
        return Response({"detail": "Ya verificado", "participant_id": participant.id}, status=200)

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
