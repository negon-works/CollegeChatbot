import re

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import ChatbotEntry, CollectedMessage

CONTACT_MARKER = "[[CONTACT_ACTIONS]]"


INTENT_RESPONSES = {
    "greeting": (
        "Hello! Welcome to the College of Engineering Aranmula assistant. "
        "How can I help you today?"
    ),
    "casual_chat": (
        "I am doing great, thanks for asking. Ready to help you with anything "
        "about the college."
    ),
    "about_college": (
        "College of Engineering Aranmula is an engineering institution located in "
        "Aranmula, Pathanamthitta district in Kerala. The college is managed by "
        "the Co-operative Academy of Professional Education (CAPE), which operates "
        "under the Government of Kerala. The college provides engineering and "
        "technical education to build strong practical and technical skills."
    ),
    "courses_list": (
        "The college offers both B.Tech and Diploma programs.\n\n"
        "B.Tech Programs:\n"
        "- Computer Science and Engineering\n"
        "- Civil Engineering\n\n"
        "Diploma Programs:\n"
        "- Cyber Forensics and Information Security\n"
        "- Electrical and Electronics Engineering\n"
        "- Electronics and Communication Engineering\n"
        "- Cloud Computing and Big Data"
    ),
    "course_details_cs": (
        "Computer Science Engineering focuses on programming, software development, "
        "algorithms, and computer systems. Students learn coding, software design, "
        "and modern computing technologies."
    ),
    "course_details_civil": (
        "Civil Engineering focuses on designing and building infrastructure such as "
        "roads, bridges, buildings, and water systems. Students learn structural "
        "design, construction methods, and environmental engineering."
    ),
    "course_details": (
        "I can share details for specific courses. For example, you can ask about "
        "Computer Science or Civil Engineering."
    ),
    "course_difficulty": (
        "Every course has its own challenges. Computer Science may require strong "
        "problem-solving skills and programming practice, while Civil Engineering "
        "involves mathematics, physics, and structural design. Choosing a course "
        "that matches your interests usually makes learning easier."
    ),
    "admission_process": (
        "Admission to B.Tech programs is usually through the KEAM entrance "
        "examination conducted by the Government of Kerala. Students participate "
        "in the centralized allotment process. Diploma admissions follow procedures "
        "set by the relevant educational authorities."
    ),
    "admission_dates": (
        "Admission dates can change each year based on official notifications. "
        "For exact opening date, last date, and allotment schedule, please check "
        "the official KEAM/authority notice and contact the college office directly."
    ),
    "eligibility": (
        "For B.Tech, students should complete higher secondary education with "
        "Physics, Chemistry, and Mathematics and qualify in the KEAM entrance exam. "
        "Diploma programs usually require completion of 10th standard."
    ),
    "fees": (
        "Fee structures can vary by course and admission category. For the most "
        "accurate and updated fee details, please contact the college office or "
        "check the official website."
    ),
    "hostel_info": (
        "Yes, the college provides hostel facilities for students. Hostels are "
        "available for both boys and girls with basic accommodation and supervision."
    ),
    "hostel_food": (
        "Hostel students usually receive breakfast, lunch, and dinner. Meals often "
        "include Kerala-style dishes like rice, curry, vegetables, and other simple "
        "balanced options."
    ),
    "campus_environment": (
        "The campus environment is generally calm and suitable for studying. "
        "Students also participate in events, sports, and technical activities."
    ),
    "campus_facilities": (
        "The campus offers a library, computer labs, engineering laboratories, "
        "a canteen, sports facilities, and spaces for events and student activities."
    ),
    "canteen_food": (
        "Yes, there is a canteen on campus with snacks, tea, coffee, and simple "
        "meals. Many students use it during breaks."
    ),
    "student_life": (
        "Student life includes academics, cultural events, sports, and technical "
        "programs. These help students build skills and enjoy college life."
    ),
    "placement": (
        "The college has a placement cell that helps students prepare for jobs and "
        "connect with recruiters through training and recruitment activities."
    ),
    "location": (
        "The college is located in Aranmula, Pathanamthitta district, Kerala. "
        "Students and visitors usually reach the campus using buses and local "
        "transport from nearby towns."
    ),
    "contact": (
        "You can contact the college at:\n"
        "Phone: 0468-2319131\n"
        "Email: principal@cearanmula.ac.in"
    ),
    "visit_campus": (
        "Visitors can usually visit the campus during working hours. It is better "
        "to call the college office beforehand for a smooth visit."
    ),
    "thanks": (
        "You are welcome. I am happy I could help. If you have more questions about "
        "the college, feel free to ask anytime."
    ),
    "goodbye": (
        "Goodbye! If you need more information about the college in the future, "
        "feel free to come back and ask. Have a great day."
    ),
    "fallback": (
        "That is an interesting question. I might not have the exact information "
        "for that yet. However, I can help with courses, admissions, hostel "
        "facilities, campus life, or contact details."
    ),
}


INTENT_PATTERNS = [
    ("greeting", [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"good morning", r"good evening"]),
    ("casual_chat", [r"how are you", r"what are you doing", r"\bnice\b", r"\bcool\b", r"interesting"]),
    ("about_college", [r"about .*college", r"college information", r"college details", r"what is this college"]),
    ("courses_list", [r"courses", r"course list", r"which branches", r"what can i study"]),
    ("course_details", [r"course details", r"tell me about"]),
    ("course_difficulty", [r"hard", r"tough", r"difficult"]),
    ("admission_dates", [r"admission date", r"admission dates", r"last date", r"opening date", r"allotment date", r"\bdates?\b"]),
    ("admission_process", [r"admission process", r"how can i join", r"how to get admission", r"admission"]),
    ("eligibility", [r"eligibility", r"who can apply", r"qualification required"]),
    ("fees", [r"\bfee\b", r"\bfees\b", r"fee structure", r"course fees"]),
    ("hostel_food", [r"hostel food", r"mess food", r"food in hostel"]),
    ("hostel_info", [r"hostel", r"stay in hostel"]),
    ("campus_environment", [r"campus environment", r"how is the campus", r"is campus good"]),
    ("campus_facilities", [r"facilities", r"library", r"labs", r"canteen available"]),
    ("canteen_food", [r"canteen", r"snacks"]),
    ("student_life", [r"student life", r"college life", r"events"]),
    ("placement", [r"placement", r"job opportunities", r"companies visiting"]),
    ("location", [r"where is the college", r"how to reach", r"college location", r"\blocation\b"]),
    ("contact", [r"contact number", r"college phone", r"email address", r"\bcontact\b"]),
    ("visit_campus", [r"visit campus", r"parents visit", r"see the college"]),
    ("thanks", [r"thank you", r"\bthanks\b"]),
    ("goodbye", [r"\bbye\b", r"goodbye", r"see you later"]),
]


FOLLOW_UPS = {
    "courses_list": "Would you like to know about admission or eligibility for these courses?",
    "hostel_info": "I can also share details about hostel food or campus facilities if you like.",
    "admission_process": "Would you like me to explain eligibility or required documents next?",
    "fees": "If you want, I can also share contact details for exact latest fee confirmation.",
    "about_college": "Would you like to explore courses, campus facilities, or student life?",
}

AFFIRMATIVE_PATTERNS = [r"\byes\b", r"\byeah\b", r"\byep\b", r"\bok\b", r"\bokay\b", r"\bsure\b"]
NEGATIVE_PATTERNS = [r"\bno\b", r"\bnope\b", r"\bnot now\b", r"\blater\b"]

CONTEXTUAL_YES_RESPONSES = {
    "courses_list": (
        "Great. Here is a quick overview for both:\n\n"
        "Admission Process:\n"
        f"{INTENT_RESPONSES['admission_process']}\n\n"
        "Eligibility:\n"
        f"{INTENT_RESPONSES['eligibility']}"
    ),
    "hostel_info": (
        "Sure. Here are both details:\n\n"
        "Hostel Food:\n"
        f"{INTENT_RESPONSES['hostel_food']}\n\n"
        "Campus Facilities:\n"
        f"{INTENT_RESPONSES['campus_facilities']}"
    ),
    "admission_process": (
        "Sure, here is eligibility first:\n\n"
        f"{INTENT_RESPONSES['eligibility']}"
    ),
    "fees": (
        "Sure. Here are the official contact details for exact latest fee confirmation:\n\n"
        f"{INTENT_RESPONSES['contact']}"
    ),
    "about_college": (
        "Sure. Here is a quick overview:\n\n"
        "Courses:\n"
        f"{INTENT_RESPONSES['courses_list']}\n\n"
        "Campus Facilities:\n"
        f"{INTENT_RESPONSES['campus_facilities']}"
    ),
}

CONTEXTUAL_SINGLE_WORDS = {
    "date": "admission_dates",
    "dates": "admission_dates",
    "eligibility": "eligibility",
    "documents": "admission_process",
}


def _normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def _detect_intent(user_text):
    text = _normalize(user_text)
    if any(word in text for word in ["computer science", "cse", "cs course"]):
        return "course_details_cs"
    if any(word in text for word in ["civil engineering", "civil course"]):
        return "course_details_civil"

    for intent, patterns in INTENT_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            return intent
    return "fallback"


def _build_response(intent):
    contact_entry = ChatbotEntry.objects.filter(intent__iexact="contact").order_by("id").first()

    def contact_values():
        if not contact_entry:
            return "", "", ""
        phone = (contact_entry.phone_number or "").strip()
        whatsapp = (contact_entry.whatsapp_number or "").strip() or phone
        email = (contact_entry.email_address or "").strip()
        return (
            phone,
            whatsapp,
            email,
        )

    if intent == "contact":
        phone, whatsapp, email = contact_values()
        base = (contact_entry.response or "").strip() if contact_entry else ""
        if not base:
            base = "You can contact the college :"
        lines = [base, CONTACT_MARKER]
        return "\n".join(lines), None

    if intent == "fallback":
        fallback_entry = (
            ChatbotEntry.objects.filter(is_active=True, intent__iexact="fallback")
            .order_by("priority", "id")
            .first()
        )
        phone, whatsapp, email = contact_values()
        intro = (
            fallback_entry.response.strip()
            if fallback_entry and fallback_entry.response.strip()
            else "Sorry, I couldn't understand your question."
        )
        lines = [
            intro,
            "",
            "Please check your spelling or try asking in a different way, as incorrect spelling may prevent the bot from finding a matching answer.",
            "",
            "If you still need help, you can contact the college directly:",
            CONTACT_MARKER,
            "",
            "If you'd like, I can still help you with these topics:",
        ]
        lines.extend(
            [
                "",
                "- Courses and Programs",
                "- Admission Process",
                "- Hostel Facilities",
                "- Campus Information",
                "- Contact Details",
                "",
                "Just type your question, and I'll do my best to help.",
            ]
        )
        return "\n".join(lines), None
    message = INTENT_RESPONSES.get(intent, INTENT_RESPONSES["fallback"])
    follow_up = FOLLOW_UPS.get(intent)
    return message, follow_up


def _match_dynamic_entry(normalized_text):
    entries = ChatbotEntry.objects.filter(is_active=True).order_by("priority", "id")
    for entry in entries:
        if entry.intent.strip().lower() == "fallback":
            continue
        for trigger in entry.trigger_list():
            if trigger and trigger in normalized_text:
                follow_up = entry.follow_up.strip() if entry.follow_up else None
                return entry.intent, entry.response, follow_up
    return None


def _is_affirmative(text):
    return any(re.search(pattern, text) for pattern in AFFIRMATIVE_PATTERNS)


def _is_negative(text):
    return any(re.search(pattern, text) for pattern in NEGATIVE_PATTERNS)


def chatbot_page(request):
    return render(request, "public/chatbot.html")


@csrf_exempt
@require_POST
def ask(request):
    question = request.POST.get("question", "")
    normalized_question = _normalize(question)
    last_followup_intent = request.session.get("last_followup_intent")

    if (
        normalized_question in CONTEXTUAL_SINGLE_WORDS
        and last_followup_intent in {"courses_list", "admission_process"}
    ):
        intent = CONTEXTUAL_SINGLE_WORDS[normalized_question]
        answer, follow_up = _build_response(intent)
    elif _is_affirmative(normalized_question) and last_followup_intent in CONTEXTUAL_YES_RESPONSES:
        intent = "context_yes"
        answer = CONTEXTUAL_YES_RESPONSES[last_followup_intent]
        follow_up = None
    elif _is_negative(normalized_question) and last_followup_intent:
        intent = "context_no"
        answer = "No problem. You can ask me anything else about courses, admissions, hostel, campus, or contact details."
        follow_up = None
    else:
        dynamic_match = _match_dynamic_entry(normalized_question)
        if dynamic_match:
            intent, answer, follow_up = dynamic_match
        else:
            intent = _detect_intent(question)
            answer, follow_up = _build_response(intent)

    if intent == "fallback" and normalized_question:
        collected, created = CollectedMessage.objects.get_or_create(
            question=normalized_question,
            defaults={"count": 1, "is_processed": False},
        )
        if not created:
            collected.count += 1
            collected.is_processed = False
            collected.save(update_fields=["count", "is_processed", "updated_at"])

    contact_entry = ChatbotEntry.objects.filter(intent__iexact="contact").order_by("id").first()
    contact_actions = None
    if intent in {"fallback", "contact"} and contact_entry:
        phone = (contact_entry.phone_number or "").strip()
        whatsapp = (contact_entry.whatsapp_number or "").strip() or phone
        email = (contact_entry.email_address or "").strip()
        contact_actions = {
            "phone": phone,
            "whatsapp": whatsapp,
            "email": email,
        }

    if follow_up:
        request.session["last_followup_intent"] = intent
    else:
        request.session.pop("last_followup_intent", None)

    return JsonResponse({"intent": intent, "answer": answer, "follow_up": follow_up, "contact_actions": contact_actions})
