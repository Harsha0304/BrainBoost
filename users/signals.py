from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils.timezone import now
from .models import UserSession

@receiver(user_logged_in)
def track_login(sender, request, user, **kwargs):
    UserSession.objects.create(
        user=user,
        login_time=now()
    )

@receiver(user_logged_out)
def track_logout(sender, request, user, **kwargs):
    session = UserSession.objects.filter(
        user=user, logout_time__isnull=True
    ).last()
    if session:
        session.logout_time = now()
        session.save()
