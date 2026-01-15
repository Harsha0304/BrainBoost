from django.urls import path
from .views import *

urlpatterns = [
    path('', register, name='register'),
    path('verify-email/', verify_email, name='verify_email'),
    path('user-approval-flow/<int:user_id>/', user_approval_flow, name='user_approval_flow'),
]
