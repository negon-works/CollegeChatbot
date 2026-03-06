from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from public.models import ChatbotEntry, CollectedMessage

from .forms import ChatbotEntryForm, CollectedMapForm

DEFAULT_BOT_ENTRIES = [
    ("chatbot", "greeting", "hello, hi, hey, good morning, good evening",
     "Hello! Welcome to the College of Engineering Aranmula assistant. How can I help you today?", "", 10),
    ("chatbot", "thanks", "thanks, thank you, thanks for help",
     "You're welcome! I'm happy I could help. If you have any more questions about the college, feel free to ask anytime.", "", 12),
    ("chatbot", "goodbye", "bye, goodbye, see you later",
     "Goodbye! If you need more information about the college in the future, feel free to come back and ask. Have a great day.", "", 13),
    ("chatbot", "fallback", "fallback",
     "Sorry, I couldn't understand your question.",
     "", 999),
    ("college", "courses_list", "courses, course list, branches, what can i study",
     "The college offers both B.Tech and Diploma programs.\n\nB.Tech Programs:\n- Computer Science and Engineering\n- Civil Engineering\n\nDiploma Programs:\n- Cyber Forensics and Information Security\n- Electrical and Electronics Engineering\n- Electronics and Communication Engineering\n- Cloud Computing and Big Data",
     "Would you like to know about admission or eligibility for these courses?", 20),
    ("college", "admission_process", "admission, admission process, join, how to get admission",
     "Admission to B.Tech programs is usually through the KEAM entrance examination conducted by the Government of Kerala. Students participate in the centralized allotment process. Diploma admissions follow procedures set by the relevant educational authorities.",
     "Would you like me to explain eligibility or required documents next?", 30),
    ("college", "admission_dates", "admission date, admission dates, last date, opening date, allotment date",
     "Admission dates can change each year based on official notifications. For exact opening date, last date, and allotment schedule, please check the official KEAM/authority notice and contact the college office directly.",
     "", 31),
    ("college", "eligibility", "eligibility, who can apply, qualification required",
     "For B.Tech, students should complete higher secondary education with Physics, Chemistry, and Mathematics and qualify in the KEAM entrance exam. Diploma programs usually require completion of 10th standard.",
     "", 32),
    ("college", "fees", "fees, fee structure, btech fees, course fees",
     "Fee structures can vary by course and admission category. For the most accurate and updated fee details, please contact the college office or check the official website.",
     "If you want, I can also share contact details for exact latest fee confirmation.", 40),
    ("college", "hostel_info", "hostel, hostel available, stay in hostel",
     "Yes, the college provides hostel facilities for students. Hostels are available for both boys and girls with basic accommodation and supervision.",
     "I can also share details about hostel food or campus facilities if you like.", 50),
    ("college", "contact", "contact, phone, email, contact number",
     "You can contact the college :", "", 60),
]

OLD_FALLBACK_TEXT = (
    "That is an interesting question. I might not have the exact information for that yet. "
    "However, I can help with courses, admissions, hostel facilities, campus life, or contact details."
)


def _is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


class StaffLoginView(LoginView):
    template_name = "staffpanel/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("staffpanel:dashboard")


@login_required
@user_passes_test(_is_staff_user)
def dashboard(request):
    context = {
        "total_entries": ChatbotEntry.objects.count(),
        "active_entries": ChatbotEntry.objects.filter(is_active=True).count(),
        "pending_collected": CollectedMessage.objects.filter(is_processed=False).count(),
    }
    return render(request, "staffpanel/dashboard.html", context)


@login_required
@user_passes_test(_is_staff_user)
def bot_content(request):
    fallback_entry, _ = ChatbotEntry.objects.get_or_create(
        intent="fallback",
        defaults={
            "category": ChatbotEntry.CATEGORY_CHATBOT,
            "trigger_keywords": "fallback",
            "response": (
                "Sorry, I couldn't understand your question."
            ),
            "follow_up": "",
            "priority": 999,
            "is_active": True,
        },
    )
    if fallback_entry.response.strip() == OLD_FALLBACK_TEXT:
        fallback_entry.response = "Sorry, I couldn't understand your question."
        fallback_entry.save(update_fields=["response", "updated_at"])
    ChatbotEntry.objects.get_or_create(
        intent="contact",
        defaults={
            "category": ChatbotEntry.CATEGORY_COLLEGE,
            "trigger_keywords": "contact, phone, email, contact number",
            "response": "You can contact the college :",
            "phone_number": "0468-2319131",
            "whatsapp_number": "",
            "email_address": "principal@cearanmula.ac.in",
            "follow_up": "",
            "priority": 60,
            "is_active": True,
        },
    )

    query = request.GET.get("q", "").strip()
    focus = request.GET.get("focus", "").strip()
    valid_categories = {ChatbotEntry.CATEGORY_CHATBOT, ChatbotEntry.CATEGORY_COLLEGE}

    if "category" in request.GET:
        raw_category = request.GET.get("category", "").strip().lower()
        category = raw_category if raw_category in valid_categories else ""
        request.session["bot_content_category"] = category
    else:
        category = (request.session.get("bot_content_category") or "").strip().lower()
        if category not in valid_categories:
            category = ""

    entries = ChatbotEntry.objects.all()
    if query:
        entries = entries.filter(Q(intent__icontains=query) | Q(trigger_keywords__icontains=query))
    if category in valid_categories:
        entries = entries.filter(category=category)

    chatbot_entries = entries.filter(category=ChatbotEntry.CATEGORY_CHATBOT)
    college_entries = entries.filter(category=ChatbotEntry.CATEGORY_COLLEGE)
    uncategorized_entries = entries.exclude(
        category__in=[ChatbotEntry.CATEGORY_CHATBOT, ChatbotEntry.CATEGORY_COLLEGE]
    )

    context = {
        "entries": entries,
        "chatbot_entries": chatbot_entries,
        "college_entries": college_entries,
        "uncategorized_entries": uncategorized_entries,
        "query": query,
        "focus": focus,
        "selected_category": category,
    }
    return render(request, "staffpanel/bot_content.html", context)


@login_required
@user_passes_test(_is_staff_user)
def bot_load_defaults(request):
    if request.method == "POST":
        for category, intent, triggers, response, follow_up, priority in DEFAULT_BOT_ENTRIES:
            entry, created = ChatbotEntry.objects.get_or_create(
                intent=intent,
                defaults={
                    "category": category,
                    "trigger_keywords": triggers,
                    "response": response,
                    "phone_number": "0468-2319131" if intent == "contact" else "",
                    "whatsapp_number": "",
                    "email_address": "principal@cearanmula.ac.in" if intent == "contact" else "",
                    "follow_up": follow_up,
                    "priority": priority,
                    "is_active": True,
                },
            )
            if not created:
                entry.category = category
                entry.trigger_keywords = triggers
                entry.response = response
                if intent == "contact":
                    if not entry.phone_number:
                        entry.phone_number = "0468-2319131"
                    if not entry.email_address:
                        entry.email_address = "principal@cearanmula.ac.in"
                entry.follow_up = follow_up
                entry.priority = priority
                entry.is_active = True
                entry.save()
    return redirect("staffpanel:bot_content")


@login_required
@user_passes_test(_is_staff_user)
def bot_entry_create(request):
    prefill_trigger = request.GET.get("prefill_trigger", "").strip()
    prefill_category = request.GET.get("category", "").strip().lower()
    collected_id = request.GET.get("collected_id", "").strip()
    initial = {}
    if prefill_trigger:
        initial["trigger_keywords"] = prefill_trigger
    if prefill_category in {ChatbotEntry.CATEGORY_CHATBOT, ChatbotEntry.CATEGORY_COLLEGE}:
        initial["category"] = prefill_category

    if request.method == "POST":
        form = ChatbotEntryForm(request.POST)
        if form.is_valid():
            form.save()
            if collected_id.isdigit():
                collected = CollectedMessage.objects.filter(id=int(collected_id)).first()
                if collected:
                    collected.delete()
            return redirect("staffpanel:bot_content")
    else:
        form = ChatbotEntryForm(initial=initial)
    focus = request.GET.get("focus", "").strip()
    return render(
        request,
        "staffpanel/bot_entry_form.html",
        {"form": form, "mode": "Create", "focus": focus, "prefill_trigger": prefill_trigger},
    )


@login_required
@user_passes_test(_is_staff_user)
def bot_entry_edit(request, entry_id):
    entry = get_object_or_404(ChatbotEntry, id=entry_id)
    if request.method == "POST":
        form = ChatbotEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("staffpanel:bot_content")
    else:
        form = ChatbotEntryForm(instance=entry)
    focus = request.GET.get("focus", "").strip()
    return render(
        request,
        "staffpanel/bot_entry_form.html",
        {"form": form, "mode": "Edit", "entry": entry, "focus": focus},
    )


@login_required
@user_passes_test(_is_staff_user)
def bot_entry_toggle(request, entry_id):
    entry = get_object_or_404(ChatbotEntry, id=entry_id)
    if entry.intent.strip().lower() in {"fallback", "contact"}:
        return redirect("staffpanel:bot_content")
    entry.is_active = not entry.is_active
    entry.save(update_fields=["is_active", "updated_at"])
    return redirect("staffpanel:bot_content")


@login_required
@user_passes_test(_is_staff_user)
def bot_entry_delete(request, entry_id):
    entry = get_object_or_404(ChatbotEntry, id=entry_id)
    if entry.intent.strip().lower() in {"fallback", "contact"}:
        return redirect("staffpanel:bot_content")
    if request.method == "POST":
        entry.delete()
        return redirect("staffpanel:bot_content")
    return render(request, "staffpanel/bot_entry_delete.html", {"entry": entry})


@login_required
@user_passes_test(_is_staff_user)
def reports(request):
    return redirect("staffpanel:dashboard")


@login_required
@user_passes_test(_is_staff_user)
def settings_page(request):
    return render(request, "staffpanel/settings.html")


@login_required
@user_passes_test(_is_staff_user)
def collected(request):
    items = CollectedMessage.objects.all()
    item_rows = [{"item": item, "form": CollectedMapForm(prefix=f"m{item.id}")} for item in items]
    return render(request, "staffpanel/collected.html", {"item_rows": item_rows, "items": items})


@login_required
@user_passes_test(_is_staff_user)
def collected_add_to_intent(request, item_id):
    item = get_object_or_404(CollectedMessage, id=item_id)
    if request.method != "POST":
        return redirect("staffpanel:collected")

    form = CollectedMapForm(request.POST, prefix=f"m{item.id}")
    if not form.is_valid():
        return redirect("staffpanel:collected")

    entry = form.cleaned_data["intent_entry"]
    existing = entry.trigger_list()
    if item.question not in existing:
        triggers = [*existing, item.question]
        entry.trigger_keywords = ", ".join(dict.fromkeys(t.strip() for t in triggers if t.strip()))
        entry.save(update_fields=["trigger_keywords", "updated_at"])

    item.delete()
    return redirect("staffpanel:collected")


@login_required
@user_passes_test(_is_staff_user)
def collected_mark_new(request, item_id):
    item = get_object_or_404(CollectedMessage, id=item_id)
    return redirect(
        f"{reverse_lazy('staffpanel:bot_entry_create')}?prefill_trigger={item.question}&category=college&collected_id={item.id}"
    )


@login_required
@user_passes_test(_is_staff_user)
def collected_remove(request, item_id):
    item = get_object_or_404(CollectedMessage, id=item_id)
    if request.method == "POST":
        item.delete()
    return redirect("staffpanel:collected")


def staff_logout(request):
    logout(request)
    return redirect("staffpanel:login")
