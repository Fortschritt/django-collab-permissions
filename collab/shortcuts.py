from guardian.shortcuts import get_objects_for_user as gofu

def get_objects_for_user(user, perms, klass=None, use_groups=True, 
        any_perm=False, with_superuser=True, accept_global_perms=True):
    """
    wrapper around guardian.shortcuts.get_objects.for_user.
    Grants full access to manager role, else falls back to default
    funcionality.

    This is a bit hacky, but right now a custom permission backend would be
    overkill.
    """

    if user.collab.is_manager and klass is not None:
        return klass.objects.all()
    else:
        return gofu(user, perms, klass, use_groups,
            any_perm, with_superuser, accept_global_perms)