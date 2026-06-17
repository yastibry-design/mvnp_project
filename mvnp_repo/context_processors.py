from .models import ResearchApplication


def applicant_notifications(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return {'applicant_count': 0}

    # Always show the live count of applications still awaiting review
    count = ResearchApplication.objects.filter(status='Pending').count()
    return {'applicant_count': count}
