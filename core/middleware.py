from django.utils.deprecation import MiddlewareMixin
from core.models import ActivityLog

class ActivityLogMiddleware(MiddlewareMixin):
    """
    Middleware to detect the logged-in user and log operations
    for production auditing.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only log authenticated write operations to reduce noise
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            ip_address = self.get_client_ip(request)
            try:
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"{request.method} {request.path}",
                    ip_address=ip_address,
                    details=f"Accessed view: {view_func.__name__}"
                )
            except Exception:
                # Fail silently to avoid interrupting the main flow
                pass
        return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
