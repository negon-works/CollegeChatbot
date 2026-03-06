from public.models import CollectedMessage


def pending_collected_context(request):
    if not request.user.is_authenticated:
        return {"pending_collected_count": 0}
    if not (request.user.is_staff or request.user.is_superuser):
        return {"pending_collected_count": 0}
    count = CollectedMessage.objects.filter(is_processed=False).count()
    return {"pending_collected_count": count}
