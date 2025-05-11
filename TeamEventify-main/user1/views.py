#for all
from django.shortcuts import render, redirect

#for login logout
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

#for signup
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib.auth.forms import AuthenticationForm

#for reset password and otp
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib import messages
from eventify.settings import EMAIL_HOST_USER
from .models import CustomUser

# ---------------------------------------------------------------------------------------------------------------------------
 
#1 Login
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("event:home")
    else:
        form = AuthenticationForm()
    
    return render(request, "user1/login.html", {"form": form})

# ---------------------------------------------------------------------------------------------------------------------------
#2 Sign up
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # login(request, user)
            return redirect("login")  # Redirect to homepage or dashboard
    else:
        form = CustomUserCreationForm()
    
    return render(request, "user1/signup.html", {"form": form})

# ---------------------------------------------------------------------------------------------------------------------------
#14 Update profile
@login_required
def update_profile(request):
    """View to update user profile with password change option"""
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)

            # Get passwords from form
            current_password = form.cleaned_data.get("current_password")
            new_password = form.cleaned_data.get("new_password")
            confirm_password = form.cleaned_data.get("confirm_password")

            if current_password and new_password:
                # If the current password is incorrect
                if not request.user.check_password(current_password):
                    messages.error(request, "❌ Current password is incorrect!")
                    return redirect("update_profile")

                # If new password and confirm password do not match
                if new_password != confirm_password:
                    messages.error(request, "❌ New password and confirm password do not match!")
                    return redirect("update_profile")

                # Update password
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep user logged in

            user.save()
            return redirect("event:profile")  # Redirect to profile page
        else:
            messages.error(request, "Please check old password or your new password and confirm password are not same.")

    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, "user1/update_profile.html", {"form": form})

# ---------------------------------------------------------------------------------------------------------------------------
#19 Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# ---------------------------------------------------------------------------------------------------------------------------
#21.1 Forgot Password

User = get_user_model()

otp_storage = {}

def send_otp(request):
    """Send OTP to the user's email for password reset."""
    if request.user.is_authenticated:
        email = request.user.email  # Get email directly if logged in
    elif request.method == "POST":
        email = request.POST.get("email")  # Get email from form input
    else:
        return render(request, "user1/forgot_password.html")

    try:
        user = CustomUser.objects.get(email=email)
        otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
        otp_storage[email] = otp  # Store OTP temporarily

        # Send OTP via email
        send_mail(
            "Password Reset OTP",
            f"Your OTP for password reset is {otp}. Do not share it with anyone.",
            EMAIL_HOST_USER, 
            [email],
            fail_silently=False,
        )
        request.session["reset_email"] = email  # Store email in session

        # Add message for the user
        messages.success(request, f"OTP has been sent to your email: {email}")

        return redirect("verify_otp")  # Redirect to OTP verification page
    except CustomUser.DoesNotExist:
        messages.error(request, "Email not found.")
        return redirect("forgot_password")

#21.2 Verify OTP
def verify_otp(request):
    """Verify the OTP entered by the user."""
    if request.method == "POST":
        email = request.session.get("reset_email")
        entered_otp = request.POST.get("otp")

        if email in otp_storage and str(otp_storage[email]) == entered_otp:
            request.session["otp_verified"] = True
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("verify_otp")

    return render(request, "user1/verify_otp.html")

#21.3 Reset Password
def reset_password(request):
    """Reset the password if OTP is verified."""
    if not request.session.get("otp_verified"):
        return redirect("forgot_password")  # Prevent unauthorized access

    if request.method == "POST":
        email = request.session.get("reset_email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user = User.objects.get(email=email)
        user.password = make_password(new_password)  # Hash the new password
        user.save()

        # Clear session and OTP storage
        request.session.flush()
        otp_storage.pop(email, None)

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "user1/reset_password.html")

# ---------------------------------------------------------------------------------------------------------------------------
