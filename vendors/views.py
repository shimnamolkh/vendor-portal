from django.shortcuts import render, redirect, get_object_or_404
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

