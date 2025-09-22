from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Participant


@shared_task
def send_verification_email_task(participant_id: int):
    p = Participant.objects.get(id=participant_id)
    token = str(p.verification_token)
    verify_url = f"{settings.FRONTEND_URL}/verify?token={token}"
    subject = "Verifica tu correo – Sorteo San Valentín"
    message = (
        f"Hola {p.full_name},\n\n"
        f"Gracias por registrarte. Verifica tu cuenta entrando a: {verify_url}\n\n"
        "Si desconoces este correo, ignora este mensaje."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [p.email])


@shared_task
def send_winner_email_task(participant_id: int):
    p = Participant.objects.get(id=participant_id)
    subject = "¡Felicidades! Eres el ganador – Sorteo San Valentín"
    message = (
        f"Hola {p.full_name},\n\n"
        "¡Felicidades! Has sido seleccionado como ganador del Sorteo San Valentín.\n"
        "Nos pondremos en contacto contigo para coordinar la entrega del premio.\n\n"
        "Saludos,\nCTS Turismo"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [p.email])
