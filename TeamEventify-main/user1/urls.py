from django.urls import path
from . import views

# localhost:8000/

urlpatterns = [
    path("", views.login_view, name="login"),  #1 Custom login view

    path("signup/", views.signup_view, name="signup"),  #2 User registration

    path("profile/update/", views.update_profile, name="update_profile"),  #14 User profile update

    path("logout/", views.logout_view, name="logout"),  #18 Logs out user and redirects to login

    path("forgot_password/", views.send_otp, name="forgot_password"), #21.1 Forgot Password
    path("verify_otp/", views.verify_otp, name="verify_otp"), #21.2 Verify OTP
    path("reset_password/", views.reset_password, name="reset_password"), #21.3 Reset Password
]