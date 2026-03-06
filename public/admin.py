from django.contrib import admin

from .models import ChatbotEntry, CollectedMessage


@admin.register(ChatbotEntry)
class ChatbotEntryAdmin(admin.ModelAdmin):
    list_display = ("intent", "category", "priority", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("intent", "trigger_keywords", "response", "email_address", "phone_number")
    ordering = ("category", "priority", "intent", "id")


@admin.register(CollectedMessage)
class CollectedMessageAdmin(admin.ModelAdmin):
    list_display = ("question", "count", "is_processed", "updated_at")
    list_filter = ("is_processed",)
    search_fields = ("question",)
    ordering = ("is_processed", "-count", "-updated_at", "-id")
