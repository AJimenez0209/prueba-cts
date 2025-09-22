from rest_framework import serializers
from .models import Participant

class ParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["full_name", "email", "phone"]

    def validate_email(self, value):
        if Participant.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value
