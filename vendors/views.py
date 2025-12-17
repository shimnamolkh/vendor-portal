from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Submission, SubmissionDocument
from .forms import SupplierInwardEntryForm, DirectPurchaseEntryForm, SupplierInwardEditForm, DirectPurchaseEditForm

@login_required
def dashboard(request):
    """Main vendor dashboard with tabs for different entry types"""
    # Get the active tab from query parameter, default to 'inward'
    active_tab = request.GET.get('tab', 'inward')
    
    # Fetch submissions for history tab
    submissions = Submission.objects.filter(vendor=request.user).prefetch_related('documents')
    
    context = {
        'active_tab': active_tab,
        'vendor': request.user,
        'submissions': submissions,
    }
    
    return render(request, 'vendors/dashboard.html', context)

@login_required
def supplier_inward_entry(request):
    """Handle supplier inward entry form submission"""
    if request.method == 'POST':
        form = SupplierInwardEntryForm(request.POST, request.FILES)
        if form.is_valid():
            # Create submission
            submission = Submission.objects.create(
                vendor=request.user,
                created_by=request.user,
                updated_by=request.user,
                submission_type='inward',
                remarks=form.cleaned_data.get('remarks', '')
            )
            
            # Save documents
            documents = [
                ('invoice', form.cleaned_data['invoice']),
                ('delivery_order', form.cleaned_data['delivery_order']),
                ('purchase_order', form.cleaned_data['purchase_order']),
            ]
            
            for doc_type, file in documents:
                SubmissionDocument.objects.create(
                    submission=submission,
                    document_type=doc_type,
                    file=file,
                    original_name=file.name,
                    file_size=file.size,
                    created_by=request.user,
                    updated_by=request.user
                )
            
            messages.success(request, 'Supplier inward entry submitted successfully!')
            return redirect('vendors:dashboard')
    else:
        form = SupplierInwardEntryForm()
    
    return render(request, 'vendors/supplier_inward_entry.html', {'form': form})

@login_required
def direct_purchase_entry(request):
    """Handle direct purchase entry form submission"""
    if request.method == 'POST':
        form = DirectPurchaseEntryForm(request.POST, request.FILES)
        if form.is_valid():
            # Create submission
            submission = Submission.objects.create(
                vendor=request.user,
                created_by=request.user,
                updated_by=request.user,
                submission_type='direct',
                remarks=form.cleaned_data.get('remarks', '')
            )
            
            # Save invoice document
            invoice = form.cleaned_data['invoice']
            SubmissionDocument.objects.create(
                submission=submission,
                document_type='invoice',
                file=invoice,
                original_name=invoice.name,
                file_size=invoice.size,
                created_by=request.user,
                updated_by=request.user
            )
            
            messages.success(request, 'Direct purchase entry submitted successfully!')
            return redirect('vendors:dashboard')
    else:
        form = DirectPurchaseEntryForm()
    
    return render(request, 'vendors/direct_purchase_entry.html', {'form': form})

@login_required
def submission_history(request):
    """Display vendor's submission history"""
    submissions = Submission.objects.filter(vendor=request.user).prefetch_related('documents')
    
    context = {
        'submissions': submissions,
    }
    
    return render(request, 'vendors/submission_history.html', context)

@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, vendor=request.user)
    
    if submission.status != 'rejected':
         messages.error(request, 'Only rejected submissions can be edited.')
         return redirect('vendors:history')

    is_inward = (submission.submission_type == 'inward')
    FormClass = SupplierInwardEditForm if is_inward else DirectPurchaseEditForm
    template = 'vendors/edit_submission.html'

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            submission.remarks = form.cleaned_data.get('remarks', '')
            submission.status = 'pending'
            # Keep verification_notes for history or clear them? 
            # Usually vendors want to see why it was rejected, but once they resubmit, it's pending again.
            # We'll leave them for now.
            submission.updated_by = request.user
            submission.save()
            
            # Update files
            file_fields = ['invoice', 'delivery_order', 'purchase_order'] if is_inward else ['invoice']
            
            for field in file_fields:
                new_file = form.cleaned_data.get(field)
                if new_file:
                    doc = submission.documents.filter(document_type=field).first()
                    if doc:
                        doc.file = new_file
                        doc.original_name = new_file.name
                        doc.file_size = new_file.size
                        doc.updated_by = request.user
                        doc.save()
                    else:
                         SubmissionDocument.objects.create(
                            submission=submission,
                            document_type=field,
                            file=new_file,
                            original_name=new_file.name,
                            file_size=new_file.size,
                            created_by=request.user,
                            updated_by=request.user
                        )
            
            messages.success(request, 'Submission updated and resubmitted successfully!')
            return redirect('vendors:dashboard')
    else:
        initial = {'remarks': submission.remarks}
        form = FormClass(initial=initial)
    
    return render(request, template, {'form': form, 'submission': submission})


# ============================================================================
# OTP AUTHENTICATION
# ============================================================================

def otp_login_view(request):
    """Render the OTP login/signup page"""
    if request.user.is_authenticated:
        if request.user.user_type == 'finance':
            return redirect('finance:dashboard')
        return redirect('vendors:dashboard')
    return render(request, 'vendors/login_otp.html')

def request_otp(request):
    """API to generate and send OTP via Email"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    import random
    import string
    from django.core.mail import send_mail
    from django.contrib.auth import get_user_model
    from core.models import OTPVerification
    from django.conf import settings
    
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    # Generate 6-digit OTP
    otp_code = ''.join(random.choices(string.digits, k=6))
    
    # Check if user exists or create new one (Verified Later)
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # User doesn't exist. We will track OTP against email.
        user = None 

    # Save OTP
    OTPVerification.objects.create(
        email=email,
        otp=otp_code,
        user=user
    )
    
    # LOG OTP for Development Convenience
    import logging
    logger = logging.getLogger('finance')
    logger.info(f"🔑 [OTP GEN] Generated OTP for {email}: {otp_code}")
    print(f"\nYour OTP Code is: {otp_code}\n")

    # Send Email
    subject = 'Your Vendor Portal OTP Code'
    message = f'Your One-Time Password (OTP) for Vendor Portal login is: {otp_code}\n\nThis code is valid for 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@vendorportal.com'
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'OTP sent to your email.'})
    except Exception as e:
        print(f"Error sending email: {e}")
        return JsonResponse({'error': 'Failed to send OTP email. Please try again.'}, status=500)

def verify_otp(request):
    """API to verify OTP and login"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    from core.models import OTPVerification
    from django.contrib.auth import login, get_user_model
    from django.utils import timezone
    from datetime import timedelta
    
    email = request.POST.get('email')
    otp_input = request.POST.get('otp')
    
    if not email or not otp_input:
        return JsonResponse({'error': 'Email and OTP are required'}, status=400)
    
    # Verify OTP
    # Must be within last 10 minutes and not verified
    time_threshold = timezone.now() - timedelta(minutes=10)
    
    otp_record = OTPVerification.objects.filter(
        email=email, 
        otp=otp_input,
        is_verified=False,
        created_at__gte=time_threshold
    ).order_by('-created_at').first()
    
    if not otp_record:
        return JsonResponse({'error': 'Invalid or expired OTP.'}, status=400)
    
    # Mark verified
    otp_record.is_verified = True
    otp_record.save()
    
    # Login or Create User
    User = get_user_model()
    created = False
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Create new vendor user
        username = email.split('@')[0]
        # Ensure unique username
        if User.objects.filter(username=username).exists():
            username = f"{username}_{otp_input}"
            
        user = User.objects.create_user(
            username=username,
            email=email,
            user_type='vendor'
        )
        created = True
    
    # Log the user in
    login(request, user)
    
    # DETERMINE REDIRECT
    # If it's a new user OR they don't have a usable password (unlikely for new but possible for old imports)
    # We redirect them to set a password.
    redirect_url = '/vendors/dashboard/'
    if created or not user.has_usable_password():
        redirect_url = '/vendors/set-password/'
    
    return JsonResponse({
        'success': True, 
        'redirect_url': redirect_url,
        'message': 'Verification successful!',
        'new_user': created
    })

@login_required
def set_password_view(request):
    """View to allow user to set their password after OTP login"""
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'vendors/set_password.html')
            
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(request, 'vendors/set_password.html')
            
        # Set password
        request.user.set_password(password)
        request.user.save()
        
        # Re-authenticate because changing password invalidates the session
        # We need the backend str usually, but since we are already logged in...
        # A simpler way is to update_session_auth_hash but let's just force a session update
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Password set successfully!")
        return redirect('vendors:dashboard')
        
    return render(request, 'vendors/set_password.html')

