from django.shortcuts import redirect
from django.urls import reverse
from datetime import date
from .models import SystemLicense

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Always allow access to the unlock page, the admin panel, and CSS styling
        allowed_paths = [reverse('unlock_system'), '/admin/']
        if any(request.path.startswith(p) for p in allowed_paths) or request.path.startswith('/static/'):
            return self.get_response(request)

        try:
            license_obj = SystemLicense.objects.first()
            # If no license exists, or if today's date is past the expiry date... Lock it!
            if not license_obj or license_obj.expiry_date < date.today():
                return redirect('unlock_system')
        except Exception:
            pass # Failsafe during initial database setup

        return self.get_response(request)