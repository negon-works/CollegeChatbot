from django.db import models


class ChatbotEntry(models.Model):
    CATEGORY_CHATBOT = "chatbot"
    CATEGORY_COLLEGE = "college"
    CATEGORY_CHOICES = (
        (CATEGORY_CHATBOT, "Chatbot"),
        (CATEGORY_COLLEGE, "College"),
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_COLLEGE)
    intent = models.CharField(max_length=80)
    trigger_keywords = models.TextField(
        help_text="Comma or new-line separated keywords (example: fees, fee structure, course fee)"
    )
    response = models.TextField()
    follow_up = models.TextField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    email_address = models.EmailField(blank=True)
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "priority", "intent", "id"]

    def __str__(self):
        return f"{self.intent} (priority {self.priority})"

    def trigger_list(self):
        raw = self.trigger_keywords.replace("\r", "\n")
        parts = []
        for chunk in raw.split("\n"):
            for item in chunk.split(","):
                token = item.strip().lower()
                if token:
                    parts.append(token)
        return parts


class CollectedMessage(models.Model):
    question = models.CharField(max_length=255, unique=True)
    count = models.PositiveIntegerField(default=1)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_processed", "-count", "-updated_at", "-id"]

    def __str__(self):
        return f"{self.question} ({self.count})"
