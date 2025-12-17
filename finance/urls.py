from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submissions/', views.submissions_list, name='submissions_list'),
    path('approve/<uuid:submission_id>/', views.approve_submission, name='approve'),
    path('reject/<uuid:submission_id>/', views.reject_submission, name='reject'),
    path('extraction/queue/', views.extraction_queue, name='extraction_queue'),
    path('extraction/start/<int:task_id>/', views.start_extraction, name='start_extraction'),
    path('extraction/view/<int:task_id>/', views.view_extraction, name='view_extraction'),
    path('extraction/compare/<int:task_id>/', views.compare_with_axpert, name='compare_with_axpert'),
    path('extraction/push/<int:task_id>/', views.push_to_axpert, name='push_to_axpert'),
]
