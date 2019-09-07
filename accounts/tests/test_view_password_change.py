from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase

class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        '''try access the password change without being logged in'''
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')

class PasswordChangeTestCase(TestCase):
    def setUp(self, data={}):
        ''' basic setup, creating a user and making a POST request to the password_change view'''
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data)

class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })
    def test_redirection(self):
        '''a valid submission should redirect the user'''
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_change_done(self):
        '''refresh the user instan ce from the db to get the hash updated by the password change'''
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        '''create a request to an abitrary page the resulting page should have '''
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def test_status_code(self):
        '''an invalid submission should return the same page'''
        self.assertEquals(self.response.status_code, 200)

    def test_form_error(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        '''refresh the instance from the db to ensure we have the latest data'''
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))