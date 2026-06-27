from django.urls import path
from .views import UserRegisterView, ChangePasswordView

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('change-password/', ChangePasswordView.as_view())
]
