from django.utils.deprecation import MiddlewareMixin

class LastActivityMiddleware(MiddlewareMixin):
    """
        Middleware to set timestamps when a user
        has been last seen
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.collab.update_last_activity()
