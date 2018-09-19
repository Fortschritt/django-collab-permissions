class LastActivityMiddleware(object):
    """
        Middlewate to set timestampe when a user
        has been last seen
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.collab.update_last_activity()
