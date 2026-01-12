from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class UserPoints(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='points'
    )
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    def update_level(self):
        self.level = (self.total_points // 100) + 1
        self.save()

    def __str__(self):
        return f"{self.user} - {self.total_points} pts"
