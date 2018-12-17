from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.functional import wraps
from guardian.compat import str
from guardian.exceptions import GuardianError
from guardian.utils import get_403_or_None
from .util import is_manager, is_space_admin_or_manager

def manager_required(func=None):
    """
    decorator for Collab views requiring at least manager rights.

    Use like stock decorators:

    @manager_required
    def my_function():
        [...]
    """
    decorator = user_passes_test(is_manager)
    if func:
        return decorator(func)
    return decorator

def space_admin_required(func):
    """
    method decorator raising 403 if user is not a space administrator in the
    current space.
    Mostly identical to the same function from django-spaces, but this one uses
    is_owner_or_admin and respects superuser privileges
    """
    def _decorator(self, *args, **kwargs):
        if self.user and self.user.is_authenticated():
            is_allowed = self.user.is_superuser
            if not is_allowed:
                is_allowed = is_space_admin_or_manager(
                    self.user, 
                    self.SPACE
                )
            if is_allowed:
                return func(self, *args, **kwargs)
        raise PermissionDenied
    return _decorator

def permission_required(perm, **kwargs):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled for the currently activated Space.

    :param login_url: if denied, user would be redirected to location set by
      this parameter. Defaults to ``django.conf.settings.LOGIN_URL``.
    :param redirect_field_name: name of the parameter passed if redirected.
      Defaults to ``django.contrib.auth.REDIRECT_FIELD_NAME``.
    :param return_403: if set to ``True`` then instead of redirecting to the
      login page, response with status code 403 is returned (
      ``django.http.HttpResponseForbidden`` instance or rendered template -
      see :setting:`GUARDIAN_RENDER_403`). Defaults to ``False``.
    :param accept_global_perms: if set to ``True``, then *object level
      permission* would be required **only if user does NOT have global
      permission** for target *model*. If turned on, makes this decorator
      like an extension over standard
      ``django.contrib.admin.decorators.permission_required`` as it would
      check for global permissions first. Defaults to ``False``.

    Examples::

        @permission_required('auth.change_user', return_403=True)
        def my_view(request):
            return HttpResponse('Hello')

    This decorator is heavily based on the ones from django-spaces.
    The difference: if user has the manager role, always return True on certain
    permissions.

    This is a bit hacky, but right now a custom permission backend would be
    overkill.
    """
    login_url = kwargs.pop('login_url', settings.LOGIN_URL)
    redirect_field_name = kwargs.pop('redirect_field_name', REDIRECT_FIELD_NAME)
    return_403 = kwargs.pop('return_403', False)
    accept_global_perms = kwargs.pop('accept_global_perms', False)
    manager_perms = ['access_space',]

    # Check if perm is given as string in order not to decorate
    # view function itself which makes debugging harder
    if not isinstance(perm, str):
        raise GuardianError("First argument must be in format: "
            "'app_label.codename or a callable which return similar string'")

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, "collab") and \
                request.user.collab.is_manager and perm in manager_perms:
                return view_func(request, *args, **kwargs)

            #if not request.user.is_authenticated():
            #    do_403 = False # enforce redirect to login for better user
            #                       # experience
            #else:
            #    do_403
            ret_403 = False if not request.user.is_authenticated() else return_403

            # if more than one parameter is passed to the decorator we try to
            # fetch object for which check would be made
            obj = request.SPACE

            response = get_403_or_None(request, perms=[perm], obj=obj,
                login_url=login_url, redirect_field_name=redirect_field_name,
                return_403=ret_403, accept_global_perms=accept_global_perms)
            if response:
                return response
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_wrapped_view)
    return decorator


def permission_required_or_403(perm, *args, **kwargs):
    """
    Identical to the decorator from django_guardian, but this one uses collabs
    permission_required function.
    """
    kwargs['return_403'] = True
    return permission_required(perm, *args, **kwargs)
