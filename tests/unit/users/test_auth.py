from unittest import TestCase
from unittest.mock import MagicMock, patch

from openslides.users.auth import AnonymousUser, auth, get_user


class TestAnonymousUser(TestCase):
    def test_get_all_permissions_from_group_1(self):
        """
        Tests, that get_all_permissions looks in the permissions of the group with
        pk=1
        """
        anonymous = AnonymousUser()

        with patch('openslides.users.auth.Permission') as mock_permission:
            anonymous.get_all_permissions()

        mock_permission.objects.filter.assert_called_once_with(group__pk=1)

    def test_has_perm_in_list(self):
        anonymous = AnonymousUser()
        anonymous.get_all_permissions = MagicMock(return_value=('p1', 'p2'))

        self.assertTrue(
            anonymous.has_perm('p1'),
            "has_perm() should return True when the user has the permission")

    def test_has_perm_not_in_list(self):
        anonymous = AnonymousUser()
        anonymous.get_all_permissions = MagicMock(return_value=('p1', 'p2'))

        self.assertFalse(
            anonymous.has_perm('p3'),
            "has_perm() should return False when the user has not the permission")

    def test_has_module_perms_in_list(self):
        anonymous = AnonymousUser()
        anonymous.get_all_permissions = MagicMock(return_value=('test_app.perm', ))

        self.assertTrue(
            anonymous.has_module_perms('test_app'),
            "has_module_perms() should return True when the user has the "
            "permission test_app.perm")

    def test_has_module_perms_not_in_list(self):
        anonymous = AnonymousUser()
        anonymous.get_all_permissions = MagicMock(return_value=('test_otherapp.perm', ))

        self.assertFalse(
            anonymous.has_module_perms('test_app'),
            "has_module_perms() should return False when the user does not have "
            "the permission test_app.perm")


@patch('openslides.users.auth.config')
@patch('openslides.users.auth._get_user')
class TestGetUser(TestCase):
    def test_not_in_cache(self, mock_get_user, mock_config):
        mock_config.__getitem__.return_value = True
        mock_get_user.return_value = AnonymousUser()
        request = MagicMock()
        del request._cached_user

        user = get_user(request)

        mock_get_user.assert_called_once_with(request)
        self.assertEqual(user, AnonymousUser())
        self.assertEqual(request._cached_user, AnonymousUser())

    def test_in_cache(self, mock_get_user, mock_config):
        request = MagicMock()
        request._cached_user = 'my_user'

        user = get_user(request)

        self.assertFalse(
            mock_get_user.called,
            "_get_user should not have been called when the user object is in cache")
        self.assertEqual(
            user,
            'my_user',
            "The user in cache should be returned")

    def test_disabled_anonymous_user(self, mock_get_user, mock_config):
        mock_config.__getitem__.return_value = False
        mock_get_user.return_value = 'django_anonymous_user'
        request = MagicMock()
        del request._cached_user

        user = get_user(request)

        mock_get_user.assert_called_once_with(request)
        self.assertEqual(
            user,
            'django_anonymous_user',
            "The django user should be returned")
        self.assertEqual(
            request._cached_user,
            'django_anonymous_user',
            "The django user should be cached")


@patch('openslides.users.auth.config')
@patch('openslides.users.auth._auth')
class TestAuth(TestCase):
    def test_anonymous_enabled(self, mock_auth, mock_config):
        mock_config.__getitem__.return_value = True
        request = MagicMock()
        mock_auth.return_value = {'user': AnonymousUser()}

        context = auth(request)

        self.assertEqual(
            context,
            {'user': AnonymousUser()})

    def test_anonymous_disabled(self, mock_auth, mock_config):
        mock_config.__getitem__.return_value = False
        request = MagicMock()
        mock_auth.return_value = {'user': AnonymousUser()}

        context = auth(request)

        self.assertEqual(
            context,
            {'user': AnonymousUser()})

    def test_logged_in_user_in_request(self, mock_auth, mock_config):
        mock_config.__getitem__.return_value = True
        request = MagicMock()
        mock_auth.return_value = {'user': 'logged_in_user'}

        context = auth(request)

        self.assertEqual(
            context,
            {'user': 'logged_in_user'})