from django.urls import path
from .views import *

urlpatterns = [
    path('', register, name='register'),
    path('verify-email/', verify_email, name='verify_email'),
    path('user-approval-flow/<int:user_id>/', user_approval_flow, name='user_approval_flow'),
    path('user-approvals/', pending_user_approvals, name='pending_user_approvals'),
    path('user-approvals/<int:user_id>/approve/', approve_user, name='approve_user')
]
