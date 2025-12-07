from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from vendors.models import Submission
from .models import ExtractionTask
from .services.ollama_service import process_invoice
import json

@login_required
def dashboard(request):
    """Finance dashboard showing only summary statistics"""
    # Check if user is finance team
    if request.user.user_type != 'finance':
        messages.error(request, 'Access denied. Finance team only.')
        return redirect('dashboard_redirect')
    
    # Calculate statistics by submission type
    from django.db.models import Count, Q
    
    # Supplier Inward statistics
    inward_stats = Submission.objects.filter(submission_type='inward').aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        approved=Count('id', filter=Q(status='approved')),
        rejected=Count('id', filter=Q(status='rejected'))
    )
    
    # Direct Purchase statistics
    direct_stats = Submission.objects.filter(submission_type='direct').aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        approved=Count('id', filter=Q(status='approved')),
        rejected=Count('id', filter=Q(status='rejected'))
    )
    
    context = {
        'inward_stats': inward_stats,
        'direct_stats': direct_stats,
    }
    
    return render(request, 'finance/dashboard.html', context)


@login_required
def submissions_list(request):
    """View filtered list of submissions"""
    # Check if user is finance team
    if request.user.user_type != 'finance':
        messages.error(request, 'Access denied. Finance team only.')
        return redirect('dashboard_redirect')
    
    # Get all submissions
    submissions = Submission.objects.all().select_related('vendor').prefetch_related('documents')
    
    # Get filter parameters
    filter_type = request.GET.get('type', None)
    filter_status = request.GET.get('status', None)
    
    # Apply filters
    if filter_type in ['inward', 'direct']:
        submissions = submissions.filter(submission_type=filter_type)
    
    if filter_status in ['pending', 'approved', 'rejected']:
        submissions = submissions.filter(status=filter_status)
    
    # Order by most recent first
    submissions = submissions.order_by('-created_at')
    
    context = {
        'submissions': submissions,
        'filter_type': filter_type,
        'filter_status': filter_status,
    }
    
    return render(request, 'finance/submissions_list.html', context)


@login_required
def approve_submission(request, submission_id):
    """Approve a submission"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        submission.status = 'approved'
        submission.verified_by = request.user
        submission.verification_notes = notes
        submission.save()
        
        messages.success(request, f'Submission {submission.id} approved successfully!')
        return redirect('finance:dashboard')
    
    return render(request, 'finance/approve_submission.html', {'submission': submission})


@login_required
def reject_submission(request, submission_id):
    """Reject a submission"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        if not notes:
            messages.error(request, 'Rejection notes are required.')
            return redirect('finance:dashboard')
        
        submission.status = 'rejected'
        submission.verified_by = request.user
        submission.verification_notes = notes
        submission.save()
        
        messages.success(request, f'Submission {submission.id} rejected.')
        return redirect('finance:dashboard')
    
    vendor_display_name = submission.vendor.vendor_name if submission.vendor.vendor_name else submission.vendor.username
    submission_id_display = str(submission.id)[:13] + '...'
    
    return render(request, 'finance/reject_submission.html', {
        'submission': submission,
        'vendor_display_name': vendor_display_name,
        'submission_id_display': submission_id_display
    })


@login_required
def start_extraction(request, submission_id):
    """Start invoice extraction for a submission"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check if extraction task already exists
    existing_task = ExtractionTask.objects.filter(submission=submission).first()
    if existing_task:
        messages.info(request, 'Extraction task already exists for this submission.')
        return redirect('finance:extraction_queue')
    
    # Create extraction task
    task = ExtractionTask.objects.create(
        submission=submission,
        status='pending'
    )
    
    # Start processing in background (for now, we'll do it synchronously)
    # In production, you'd use Celery or similar
    result = process_invoice(submission)
    
    if result['success']:
        task.status = 'completed'
        task.extracted_data = result['data']
        task.processing_time = result.get('processing_time', 0)
        task.model_used = result.get('model', task.model_used)
        messages.success(request, 'Invoice extraction completed successfully!')
    else:
        task.status = 'failed'
        task.error_log = result.get('error', 'Unknown error')
        messages.error(request, f'Extraction failed: {task.error_log}')
    
    task.save()
    
    return redirect('finance:extraction_queue')


@login_required
def extraction_queue(request):
    """View extraction queue"""
    if request.user.user_type != 'finance':
        messages.error(request, 'Access denied. Finance team only.')
        return redirect('dashboard_redirect')
    
    # Get all extraction tasks
    tasks = ExtractionTask.objects.select_related(
        'submission', 'submission__vendor'
    ).order_by('-created_at')
    
    # Get submissions that don't have extraction tasks yet (approved ones)
    approved_submissions = Submission.objects.filter(
        status='approved'
    ).exclude(
        id__in=tasks.values_list('submission_id', flat=True)
    ).select_related('vendor').prefetch_related('documents')
    
    context = {
        'tasks': tasks,
        'approved_submissions': approved_submissions,
    }
    
    return render(request, 'finance/extraction_queue.html', context)


@login_required
def view_extraction(request, task_id):
    """View extraction task details"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    task = get_object_or_404(ExtractionTask, id=task_id)
    
    # Pretty print JSON data
    if task.extracted_data:
        formatted_data = json.dumps(task.extracted_data, indent=2)
    else:
        formatted_data = None
    
    context = {
        'task': task,
        'formatted_data': formatted_data,
    }
    
    return render(request, 'finance/view_extraction.html', context)
