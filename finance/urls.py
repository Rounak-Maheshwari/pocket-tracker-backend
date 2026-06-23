from .views import AccountListCreateView, ListAccountTypesView, AccountUpdateDeleteView
from django.urls import path


urlpatterns = [
    path('list-create-account/', AccountListCreateView.as_view()),
    path('update-account/<int:pk>', AccountUpdateDeleteView.as_view()),
]