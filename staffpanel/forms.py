from django import forms

from public.models import ChatbotEntry


class ChatbotEntryForm(forms.ModelForm):
    class Meta:
        model = ChatbotEntry
        fields = [
            "category",
            "intent",
            "trigger_keywords",
            "response",
            "phone_number",
            "whatsapp_number",
            "email_address",
            "follow_up",
            "priority",
            "is_active",
        ]
        widgets = {
            "category": forms.Select(),
            "intent": forms.TextInput(attrs={"placeholder": "Example: fees"}),
            "trigger_keywords": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "fees, fee structure, course fee",
                }
            ),
            "response": forms.Textarea(attrs={"rows": 6}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+91 XXXXX XXXXX"}),
            "whatsapp_number": forms.TextInput(attrs={"placeholder": "+91 XXXXX XXXXX"}),
            "email_address": forms.EmailInput(attrs={"placeholder": "info@college.edu"}),
            "follow_up": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional"}),
            "priority": forms.NumberInput(attrs={"min": 1}),
        }


class CollectedMapForm(forms.Form):
    intent_entry = forms.ChoiceField(choices=(), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        entries = ChatbotEntry.objects.exclude(intent__iexact="fallback").order_by("category", "priority", "intent", "id")
        college = [(str(e.id), e.intent) for e in entries if e.category == ChatbotEntry.CATEGORY_COLLEGE]
        chatbot = [(str(e.id), e.intent) for e in entries if e.category == ChatbotEntry.CATEGORY_CHATBOT]
        others = [
            (str(e.id), e.intent)
            for e in entries
            if e.category not in {ChatbotEntry.CATEGORY_COLLEGE, ChatbotEntry.CATEGORY_CHATBOT}
        ]

        choices = [("", "Select intent")]
        if college:
            choices.append(("College", college))
        if chatbot:
            choices.append(("Chatbot", chatbot))
        if others:
            choices.append(("Other", others))
        self.fields["intent_entry"].choices = choices

    def clean_intent_entry(self):
        entry_id = self.cleaned_data["intent_entry"]
        entry = ChatbotEntry.objects.filter(id=entry_id).exclude(intent__iexact="fallback").first()
        if not entry:
            raise forms.ValidationError("Please select a valid intent.")
        return entry
