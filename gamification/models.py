from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# =========================
# USER POINTS & LEVELS
# =========================
class UserPoints(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='points'
    )
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    def add_points(self, points):
        """Add points and auto-update level"""
        self.total_points += points
        self.update_level()
        self.save()

    def update_level(self):
        # Level up every 100 points
        self.level = (self.total_points // 100) + 1

    def __str__(self):
        return f"{self.user} - {self.total_points} pts (Lv {self.level})"

# =========================
# BADGES
# =========================
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=50,
        help_text="Emoji or icon class (e.g. 🔥, 🏆, 🎓)"
    )
    points_required = models.PositiveIntegerField()

    def __str__(self):
        return self.name

# =========================
# USER BADGES (M2M)
# =========================
class UserBadge(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user} earned {self.badge.name}"
