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
    """Approve a submission and automatically start extraction"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        submission.status = 'approved'
        submission.verified_by = request.user
        submission.verification_notes = notes
        submission.updated_by = request.user
        submission.save()
        
        # Automatically create extraction task and start processing
        from .models import ExtractionTask
        import threading
        from django.db import connection

        def run_extraction_background(task_id):
            # This function runs in a thread
            # Create a new connection for this thread
            from .models import ExtractionTask
            # We need to manually manage connection in thread
            
            try:
                task = ExtractionTask.objects.get(id=task_id)
                # Re-import to avoid scope issues
                from .services.ollama_service import process_invoice
                
                result = process_invoice(task.submission)
                
                if result['success']:
                    task.status = 'completed'
                    task.extracted_data = result['data']
                    task.processing_time = result.get('processing_time', 0)
                    task.model_used = result.get('model', task.model_used)
                else:
                    task.status = 'failed'
                    task.error_log = result.get('error', 'Unknown error')
                
                task.save()
            except Exception as e:
                print(f"Extraction thread error: {e}")
                # Try to log failure to task if possible
                try:
                    task = ExtractionTask.objects.get(id=task_id)
                    task.status = 'failed'
                    task.error_log = f"System Error: {str(e)}"
                    task.save()
                except:
                    pass
            finally:
                connection.close()

        existing_task = ExtractionTask.objects.filter(submission=submission).first()
        
        if not existing_task:
            # Create extraction task with processing status
            task = ExtractionTask.objects.create(
                submission=submission,
                status='processing'
            )
            # Start background thread
            thread = threading.Thread(target=run_extraction_background, args=(task.id,))
            thread.daemon = True
            thread.start()
            
            messages.success(request, f'Submission approved! Extraction started automatically.')
        else:
            # If task exists (maybe from previous run), restart it
            existing_task.status = 'processing'
            existing_task.error_log = ''
            existing_task.save()
            
            thread = threading.Thread(target=run_extraction_background, args=(existing_task.id,))
            thread.daemon = True
            thread.start()
            
            messages.success(request, f'Submission approved! Extraction restarted.')
        
        # Redirect back to submissions list to allow approving next item
        return redirect('finance:submissions_list')
    
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
        submission.updated_by = request.user
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
def start_extraction(request, task_id):
    """Process a pending extraction task"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    from .models import ExtractionTask
    task = get_object_or_404(ExtractionTask, id=task_id)
    
    if task.status not in ['pending', 'failed', 'processing']:
        messages.info(request, 'This extraction task has already been processed.')
        return redirect('finance:extraction_queue')
    
    # Update status to processing and clear previous errors
    task.status = 'processing'
    task.error_log = ''  # Clear previous errors (must be empty string, not None)
    task.save()
    
    # Process the invoice
    result = process_invoice(task.submission)
    
    if result['success']:
        task.status = 'completed'
        task.extracted_data = result['data']
        task.processing_time = result.get('processing_time', 0)
        task.model_used = result.get('model', task.model_used)
        messages.success(request, 'Invoice extraction completed successfully!')
    else:
        task.status = 'failed'
        task.error_log = result.get('error', 'Unknown error')
        # Show a friendly message to the user, keep technical details in the task log
        messages.error(request, 'Extraction failed. Please review the error log on the task card.')
    
    task.save()
    
    return redirect('finance:extraction_queue')


@login_required
def compare_with_axpert(request, task_id):
    """Show extracted data compared with Axpert database data"""
    if request.user.user_type != 'finance':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    from .models import ExtractionTask
    task = get_object_or_404(ExtractionTask, id=task_id)
    
    if task.status != 'completed':
        messages.error(request, 'Extraction must be completed before comparing with Axpert.')
        return redirect('finance:extraction_queue')
    
    # Format data for display
    formatted_data = json.dumps(task.extracted_data, indent=2)
    
    # Pre-process Axpert data for easier template rendering
    axpert_display = {}
    if 'axpert_data' in task.extracted_data:
        ax_data = task.extracted_data['axpert_data']
        
        # Process Vendor Data: Convert columns/rows to dictionary
        if 'vendor' in ax_data and ax_data['vendor'].get('rows') and ax_data['vendor'].get('columns'):
            rows = ax_data['vendor']['rows']
            cols = ax_data['vendor']['columns']
            if rows:
                # Take the first row and zip with columns
                axpert_display['vendor'] = dict(zip(cols, rows[0]))
        
        # Keep PO data structure for table display
        if 'po' in ax_data:
            axpert_display['po'] = ax_data['po']

    context = {
        'task': task,
        'submission': task.submission,
        'extracted_data': task.extracted_data,
        'formatted_data': formatted_data,
        'axpert_display': axpert_display,
        'po_number': task.extracted_data.get('PO_Number', ''),
        'processing_time': task.processing_time,
        'has_axpert_data': 'axpert_data' in task.extracted_data,
    }
    
    return render(request, 'finance/compare_with_axpert.html', context)


@login_required
def extraction_queue(request):
    """View extraction queue"""
    if request.user.user_type != 'finance':
        messages.error(request, 'Access denied. Finance team only.')
        return redirect('dashboard_redirect')
    
    from django.utils import timezone
    from datetime import datetime
    
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
    
    # Calculate metrics
    today = timezone.now().date()
    pending_count = tasks.filter(status='pending').count()
    processing_count = tasks.filter(status='processing').count()
    completed_today_count = tasks.filter(
        status='completed',
        updated_at__date=today
    ).count()
    
    context = {
        'tasks': tasks,
        'approved_submissions': approved_submissions,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'completed_today_count': completed_today_count,
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
