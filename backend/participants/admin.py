from django.contrib import admin
from .models import Participant

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "is_verified", "created_at")
    search_fields = ("full_name", "email")
    list_filter = ("is_verified", "created_at")
