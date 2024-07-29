# urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import login_view, register_user, CustomPasswordResetView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        form_class=CustomPasswordResetForm
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
