from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('supplier-inward/', views.supplier_inward_entry, name='supplier_inward'),
    path('direct-purchase/', views.direct_purchase_entry, name='direct_purchase'),
    path('history/', views.submission_history, name='history'),
    path('edit/<uuid:submission_id>/', views.edit_submission, name='edit_submission'),
    path('login/', views.otp_login_view, name='login_otp'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('set-password/', views.set_password_view, name='set_password'),
]
