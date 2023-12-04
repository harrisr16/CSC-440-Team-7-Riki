import os
import json
import unittest
from Riki import create_app
from wiki.web.forms import RegistrationForm
from wiki.web.user import UserManager, User

class registrationTests(unittest.TestCase):

    def create_app(self):
        directory = os.getcwd()
        app = create_app(directory)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.manager = UserManager(os.path.join(os.getcwd(), 'user'))

    def tearDown(self):
        pass

    def test_user_registration_valid_credentials(self):
        #Attempt to create valid new user account
        response = self.client.post('/register/', data=dict(
            username='newuser',
            password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
        #Check to ensure account was registered successfully
        self.assertIn(b'Registration and login successful.', response.data)

    def test_user_registration_existing_username(self):
        #Attempt to create a new account with my username
        response = self.client.post('/register/', data=dict(
            username='kenny',
            password='testpassword',
            confirm_password='testpassword'
        ), follow_redirects=True)
        #Check to ensure account was not registered
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', response.data)

    def test_user_registration_blank_username(self):
        #Attempt to create an account with a blank username
        response = self.client.post('/register/', data=dict(
            username='',  # Leave the username field blank
            password='testpassword',
            confirm_password='testpassword'
        ), follow_redirects=True)
        #Check to ensure registration is unsuccessful
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', response.data)

    def test_password_left_blank(self):
        #Attempt to create account without a password
        response = self.client.post('/register/', data=dict(
            username='JSON1',  # Leave the username field blank
            password='',
            confirm_password='testpassword'
        ), follow_redirects=True)
        #Check to ensure registration was unsuccessful
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', response.data)

    def test_confirm_password_left_blank(self):
        #Attempt to register account without confirm password
        response = self.client.post('/register/', data=dict(
            username='newuser1',
            password='PASSWORD',
            confirm_password=''
        ), follow_redirects=True)
        #Check to ensure registration was unsuccessful
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', response.data)

    def test_passwords_dont_match(self):
        #Attempt to register account without matching passwords
        response = self.client.post('/register/', data=dict(
            username='newuser2',  # Leave the username field blank
            password='testpassword',
            confirm_password='testpassword2'
        ), follow_redirects=True)
        #Check to ensure registration was unsuccessful
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', response.data)




"""
OUTPUT FROM TESTS:

/Users/Kenny/PycharmProjects/pythonProject/venv/bin/python /Applications/PyCharm.app/Contents/plugins/python/helpers/pycharm/_jb_pytest_runner.py --target registrationTests.py::registrationTests 
Testing started at 9:25 PM ...
Launching pytest with arguments registrationTests.py::registrationTests --no-header --no-summary -q in /Users/Kenny/PycharmProjects/pythonProject/tests

============================= test session starts ==============================
collecting ... collected 6 items

registrationTests.py::registrationTests::test_confirm_password_left_blank 
registrationTests.py::registrationTests::test_password_left_blank 
registrationTests.py::registrationTests::test_passwords_dont_match 
registrationTests.py::registrationTests::test_user_registration_blank_username 
registrationTests.py::registrationTests::test_user_registration_existing_username 
registrationTests.py::registrationTests::test_user_registration_valid_credentials 

======================== 6 passed, 2 warnings in 0.80s =========================
PASSED [ 16%]PASSED [ 33%]PASSED [ 50%]PASSED [ 66%]PASSED [ 83%]PASSED [100%]
Process finished with exit code 0

"""