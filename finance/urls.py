from .views import AccountListCreateView, ListAccountTypesView, AccountUpdateDeleteView, TransactionTypeListView, TransactionCategoryListView, TransactionCreateListView, TrnasactionUpdateDeleteView, FinancialAnalyticsListView
from django.urls import path


urlpatterns = [
    path('list-account-categories/', ListAccountTypesView.as_view()),
    path('list-create-account/', AccountListCreateView.as_view()),
    path('update-account/<int:pk>', AccountUpdateDeleteView.as_view()),
    path('transaction/transaction-types/', TransactionTypeListView.as_view()),
    path('transaction/transaction-category/', TransactionCategoryListView.as_view()),
    path('transaction/list-create/', TransactionCreateListView.as_view()),
    path('transaction/update-delete/<int:pk>', TrnasactionUpdateDeleteView.as_view()),
    path('financial-analytics/', FinancialAnalyticsListView.as_view()),
]