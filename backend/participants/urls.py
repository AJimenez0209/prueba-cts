from django.urls import path
from .views import register, verify_token, set_password, debug_celery, admin_participants, admin_draw

urlpatterns = [
    path("participants/register/", register),
    path("participants/verify/<uuid:token>/", verify_token),
    path("participants/set-password/<int:participant_id>/", set_password),
    path("debug/celery/", debug_celery),  # Ruta para verificar si se usa Celery

      # Admin API
    path("admin/participants/", admin_participants),  # GET con X-API-Key
    path("admin/draw/", admin_draw),                  # POST con X-API-Key
]

