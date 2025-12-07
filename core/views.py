from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return redirect('login')

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.user_type == 'finance':
        return redirect('finance:dashboard')
    else:
        # Default to vendor dashboard
        return redirect('vendors:dashboard')
