try:
    from unittest import mock
except ImportError:
    import mock

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from spaces.models import Space
#from .models import Collab
from .util import is_manager
from .decorators import manager_required, permission_required_or_403, space_admin_required


class TestCollabExtension(TestCase):
    """
    On creation of a user instance, a Collab instance referencing the user
    instance is supposed to be created, too (through the post_save signal).
    Assert that.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def has_attr_collab(self):
        """
        test existance of the collab extension
        """
        self.assertIs(hasattr(self.user, 'collab'), True)

    def manager_is_false(self):
        """
        by default, the user should not be a manager
        """
        self.assertIs(self.user.collab.is_manager, False)
    


class TestIsManager(TestCase):
    """
    Test the .util is_manager function.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_with_normal_user(self):
        result = is_manager(self.user)
        self.assertEqual(result, False)

    def test_with_anonymous_user(self):
        user = AnonymousUser()
        result = is_manager(user)
        self.assertEqual(result, False)

    def test_with_superuser(self):
        self.user.is_superuser = True
        result = is_manager(self.user)
        self.assertEqual(result, True)

    def test_with_manager(self):
        self.user.is_superuser = False
        self.user.collab.is_manager = True
        result = is_manager(self.user)
        self.assertEqual(result, True)


class TestRedirectToLogin(TestCase):
    """
    test the @permission_required_or_403 decorator:
    if logged in and not enough permisssions: return 403
    if not logged in and not enough permissions: return redirect to login
    if logged in and enough permissions: return 200
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        another_user = User.objects.create_user(username="a", email="a@...", password="a")
        self.space = Space.objects.create(name="My new Space", created_by=self.user)
        self.user.groups.add(self.space.get_members())
        self.another_space = Space.objects.create(name="My second new Space", created_by=another_user)

    def call_decorated_view(self,
                            is_authenticated = True, 
                            is_manager = False, 
                            is_superuser = False,
                            correct_space = False):
        request = self.factory.get('/')
        if is_authenticated:
            request.user = self.user
            request.user.is_superuser = is_superuser
            request.user.collab.is_manager = is_manager
        else:
            request.user = AnonymousUser()
        request.SPACE = self.space if correct_space else self.another_space
        request_args = []
        request_kwargs = {}
        #view = mock.MagicMock(return_value="view called")
        #decoratr = permission_required_or_403(perm="access_space")
        #decorated = decoratr(view)
        #response = decorated(request, *request_args, **request_kwargs)
        #return response, request, view, request_args, request_kwargs
        @permission_required_or_403(perm="access_space")
        def test_view(request):
            return HttpResponse("ok")
        response = test_view(request)
        return response, request

    def test_permission_required_with_anonymous_user(self):
        response, request = \
                self.call_decorated_view(is_authenticated = False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/")    

    def test_permission_required_with_logged_in_user_and_wrong_space(self):
        response, request = \
                self.call_decorated_view(is_authenticated = True)
        self.assertEqual(response.status_code, 403)

    def test_permission_required_with_logged_in_user_and_correct_space(self):
        response, request = \
                self.call_decorated_view(is_authenticated = True, correct_space = True)
        self.assertEqual(response.status_code, 200)

    

class TestManagerRequired(TestCase):
    """
    test the @manager_required decorator.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def call_decorated_view(self,
                            is_authenticated = True, 
                            is_manager = False, 
                            is_superuser = False):
        request = self.factory.get('/')
        if is_authenticated:
            request.user = self.user
            request.user.is_superuser = is_superuser
            request.user.collab.is_manager = is_manager
        else:
            request.user = AnonymousUser()
        request_args = []
        request_kwargs = {}        
        view = mock.MagicMock(return_value="view called")
        decorated = manager_required(view)
        response = decorated(request, *request_args, **request_kwargs)
        return response, request, view, request_args, request_kwargs

    def test_manager_required_with_anonymous_user(self):
        response, request, view, request_args, request_kwargs = \
                self.call_decorated_view(is_authenticated = False)
        # the anonymous user obviously is not a manager
        view.assert_not_called()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/")    

    def test_manager_required_with_user(self):
        response, request, view, request_args, request_kwargs = \
                self.call_decorated_view()
        # a normal user is no manager, so the decorator should block access to the view
        view.assert_not_called()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/")

    def test_manager_required_with_manager(self):
        response, request, view, request_args, request_kwargs = \
                self.call_decorated_view(is_manager = True)
        # manager should be let through
        view.assert_called_once_with(request, *request_args, **request_kwargs)
        self.assertEqual(response, "view called")


class SpaceAdminRequired(TestCase):
    """
    test the @space_admin_required decorator.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='a', email='a@…', password='top_secret')
        self.space = Space.objects.create(name="My new Space", created_by=self.user)

    def call_decorated_view(self,
                            is_authenticated = True,
                            is_admin = False,
                            is_manager = False, 
                            is_superuser = False):
        request = self.factory.get('/')
        if is_authenticated:
            request.user = self.user
            request.user.is_superuser = is_superuser
            request.user.collab.is_manager = is_manager
        else:
            request.user = AnonymousUser()
        if is_admin:
            self.space.get_admins().user_set.add(request.user)
        request.SPACE = self.space
        request_args = []
        request_kwargs = {}        
        view = mock.MagicMock(return_value="view called")
        decorated = space_admin_required(view)
        response = decorated(request, *request_args, **request_kwargs)
        return response, request, view, request_args, request_kwargs

    def test_space_admin_required_with_anonymous_user(self):
        # the anonymous user obviously is not an admin
        self.assertRaises(PermissionDenied, self.call_decorated_view, is_authenticated = False)

    def test_space_admin_required_with_user(self):
        # a normal user is no space admin, so the decorator should block access to the view
        self.assertRaises(PermissionDenied, self.call_decorated_view)

    def test_space_admin_required_with_space_admin(self):
        response, request, view, request_args, request_kwargs = \
                self.call_decorated_view(is_admin = True)
        # space_admin should be let through
        view.assert_called_once_with(request, *request_args, **request_kwargs)
        self.assertEqual(response, "view called")

    def test_space_admin_required_with_manager(self):
        response, request, view, request_args, request_kwargs = \
                self.call_decorated_view(is_manager = True)
        # manager should be let through
        view.assert_called_once_with(request, *request_args, **request_kwargs)
        self.assertEqual(response, "view called")
        