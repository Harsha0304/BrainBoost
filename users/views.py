from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import UserApprovalLog
from administration.models import EmailOTP
from django.core.mail import send_mail
import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import User
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.email_verified = False
            user.role = 'STUDENT'
            user.save()

            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(user=user, otp=otp)

            send_mail(
                subject="Verify your email",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            return redirect('verify_email')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def user_approval_flow(request, user_id):
    if request.user.role != 'ADMIN':
        return HttpResponseForbidden("You are not allowed to approve users.")

    user_to_approve = get_object_or_404(User, id=user_id)

    if not user_to_approve.email_verified:
        return HttpResponseForbidden("User email not verified.")

    if request.method == 'POST':
        user_to_approve.is_active = True
        user_to_approve.save(update_fields=['is_active'])
        UserApprovalLog.objects.create(
            user=user_to_approve,
            approved_by=request.user
        )
        return redirect('dashboard')

    return render(
        request,
        'user_approval_flow.html',
        {'user': user_to_approve}
    )

def verify_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
            email_otp = EmailOTP.objects.filter(
                user=user, otp=otp, is_used=False
            ).latest('created_at')

            if email_otp.is_expired():
                messages.error(request, "OTP expired")
                return redirect('verify_email')

            email_otp.is_used = True
            email_otp.save()

            user.email_verified = True
            user.save()

            messages.success(
                request,
                "Email verified successfully. Await admin approval."
            )
            return redirect('login')

        except Exception:
            messages.error(request, "Invalid OTP")
            return redirect('verify_email')

    return render(request, 'verify_email.html')