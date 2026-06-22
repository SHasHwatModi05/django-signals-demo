from django.urls import path
from . import views

app_name = 'signals_demo'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('test/sync-async/', views.test_sync_async, name='test_sync_async'),
    path('test/thread-check/', views.test_thread_check, name='test_thread_check'),
    path('test/transaction-check/', views.test_transaction_check, name='test_transaction_check'),
    path('test/rectangle/', views.test_rectangle, name='test_rectangle'),
]
