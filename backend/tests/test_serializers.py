
import pytest
from participants.serializers import ParticipantCreateSerializer

@pytest.mark.django_db
def test_participant_create_serializer_valid():
    data = {"full_name": "Ana Pérez", "email": "ana@example.com", "phone": "+56 9 1234 5678"}
    s = ParticipantCreateSerializer(data=data)
    assert s.is_valid(), s.errors

@pytest.mark.django_db
def test_participant_create_serializer_duplicate_email(django_user_model):
    # asumiendo unique en email o validación en serializer
    from participants.models import Participant
    Participant.objects.create(full_name="X", email="dup@example.com", phone="1", is_verified=False)
    data = {"full_name": "Y", "email": "dup@example.com", "phone": "2"}
    s = ParticipantCreateSerializer(data=data)
    assert not s.is_valid()
    assert "email" in s.errors
