class FilesPermissions(object):
    
    def has_read_permission(self, request, path):
        """
        Just return True if the user is an authenticated staff member.
        Extensions could base the permissions on the path too.
        """
        user = request.user
        if user.is_anonymous:
            return False
        # outside of space, e.g. user profile pictures
        if not hasattr(request,"SPACE") or not request.SPACE:
            return True
        # else obey space membership
        return True if user.has_perm('access_space', request.SPACE) else False
