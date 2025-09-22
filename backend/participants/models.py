from django.db import models
from django.contrib.auth.hashers import make_password
import uuid

class Participant(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    password_hash = models.CharField(max_length=128, blank=True)  # se setea tras verificar
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)
        self.save(update_fields=["password_hash"])

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
