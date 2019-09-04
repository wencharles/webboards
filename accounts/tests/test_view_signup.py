from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..views import signup
from ..forms import SignUpForm

class SignUpTest(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_sign_up_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_sign_up_resolves_sign_up_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        '''
        The view must contain five inputs: csrf, username, email, password1, password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirection(self):
        '''A valid redirection should direct the user to the homepage'''
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        '''create a test to an abitrary page and the resulting page must have a user to its context after a successful login'''
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidSignUptests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.post(url, {})

    def test_status_code(self):
        '''an invalid post should return the same page'''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        '''the repsonse form should hac=ve errors'''
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())

