from django.urls import path
from .views import register, verify_token, set_password

urlpatterns = [
    path("participants/register/", register),
    path("participants/verify/<uuid:token>/", verify_token),
    path("participants/set-password/<int:participant_id>/", set_password),
]
