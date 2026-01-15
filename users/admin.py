from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from .models import UserApprovalLog

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'email_verified',
        'is_active',
        'date_joined',
    )

    list_filter = ('role', 'email_verified', 'is_active')
    search_fields = ('username', 'email')
    actions = ['approve_selected_users']

    @admin.action(description="Approve selected users")
    def approve_selected_users(self, request, queryset):
        approved_count = 0
        skipped_count = 0

        for user in queryset:
            # Business rules
            if (
                user.role != 'STUDENT'
                or user.is_active
                or not user.email_verified
            ):
                skipped_count += 1
                continue

            user.is_active = True
            user.save(update_fields=['is_active'])

            UserApprovalLog.objects.create(
                user=user,
                approved_by=request.user
            )

            approved_count += 1

        if approved_count:
            self.message_user(
                request,
                f"{approved_count} user(s) approved successfully.",
                level=messages.SUCCESS
            )

        if skipped_count:
            self.message_user(
                request,
                f"{skipped_count} user(s) were skipped (already active, "
                f"email not verified, or not students).",
                level=messages.WARNING
            )


@admin.register(UserApprovalLog)
class UserApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved_by', 'approved_at')
    list_filter = ('approved_at',)
    search_fields = ('user__username', 'approved_by__username')