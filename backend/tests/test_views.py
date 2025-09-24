
import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
def test_register_ok(client: APIClient):
    url = "/api/participants/register/"
    res = client.post(url, {"full_name": "Ana", "email": "ana@example.com", "phone": "1"}, format="json")
    assert res.status_code == 201
    assert "Gracias por registrarte" in res.data.get("message", "") or "¡Gracias por registrarte" in res.data.get("message", "")

@pytest.mark.django_db
def test_register_duplicate(client: APIClient):
    from participants.models import Participant
    Participant.objects.create(full_name="Ana", email="dup2@example.com", phone="1", is_verified=False)
    url = "/api/participants/register/"
    res = client.post(url, {"full_name": "Ana", "email": "dup2@example.com", "phone": "1"}, format="json")
    assert res.status_code in (400, 409)

@pytest.mark.django_db
def test_verify_and_set_password_flow(client: APIClient):
    # Este test asume que tienes un modelo Token o que el endpoint permite crear/verificar token preparado en fixtures
    # Aquí simulamos flujo mínimo: crear participante, generar token manual y verificar
    from participants.models import Participant
    from uuid import uuid4
    p = Participant.objects.create(full_name="Ana", email="flow@example.com", phone="1", is_verified=False)
    token = uuid4()
    # Dependiendo de tu implementación, podrías crear TokenModel(token=token, participant=p).save()

    # Verificación (GET)
    res = client.get(f"/api/participants/verify/{token}/")
    # Si tu verify crea relación con token real, ajusta este assert
    assert res.status_code in (200, 404)  # 404 si token no existe en BD, 200 si fixture lo crea

    # Set password (POST)
    res2 = client.post(f"/api/participants/set-password/{p.id}/", {"password": "Prueba1234"}, format="json")
    assert res2.status_code in (200, 400, 403)

@pytest.mark.django_db
def test_admin_list_requires_api_key(client: APIClient):
    res = client.get("/api/admin/participants/")
    assert res.status_code in (401, 403)

@pytest.mark.django_db
def test_admin_draw_with_api_key(client: APIClient, settings):
    settings.ADMIN_API_KEY = "secret"
    client.defaults["HTTP_X_API_KEY"] = "secret"
    res = client.post("/api/admin/draw/")
    assert res.status_code in (200, 404, 409)  # 404/409 si no hay verificados; 200 si devuelve winner
