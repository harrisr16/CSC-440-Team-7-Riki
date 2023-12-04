import os
import unittest
from Riki import create_app
from wiki.web.user import UserManager

class PasswordTests(unittest.TestCase):

    def create_app(self):
        directory = os.getcwd()
        app = create_app(directory)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.manager = UserManager(os.path.join(os.getcwd(), 'unit/user'))

    def tearDown(self):
        pass

    def test_change_password_valid_credentials(self):
        # Log in with the existing password
        login_response = self.client.post('/user/login/', data=dict(
            name='kenny',
            password='1234'
        ), follow_redirects=True)

        #print("Login Response:", login_response.data.decode('utf-8'))

        # Change the password
        response = self.client.post('/changepass/', data=dict(
            name='kenny',
            password='1234',
            new_password='newtestpassword'
        ), follow_redirects=True)

        #print("Password Change Response:", response.data.decode('utf-8'))

        self.client.get('/user/logout/')

        # Log in with the new password
        login_response1 = self.client.post('/user/login/', data=dict(
            name='kenny',
            password='newtestpassword'
        ), follow_redirects=True)


        #Check for successful login after password change
        self.assertIn(b'Login successful', login_response1.data)

    def test_change_password_incorrect_password(self):
        # Log in with the existing password
        login_response = self.client.post('/user/login/', data=dict(
            name='sam',
            password='1234'
        ), follow_redirects=True)

        #Check to ensure initial login is successful
        self.assertIn(b'Login successful', login_response.data)

        # Change the password
        change_response = self.client.post('/changepass/', data=dict(
            name='sam',
            password='5678',
            new_password='newtestpassword'
        ), follow_redirects=True)

        #Check to make sure password change does not occur
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', change_response.data)

    def test_change_password_old_left_blank(self):
        # Log in with the existing password
        login_response = self.client.post('/user/login/', data=dict(
            name='sam',
            password='1234'
        ), follow_redirects=True)

        # Change the password
        change_response = self.client.post('/changepass/', data=dict(
            name='sam',
            password='',
            new_password='newtestpassword'
        ), follow_redirects=True)

        #Check to make sure password change does not occur
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', change_response.data)

    def test_change_password_new_password_blank(self):
        # Log in with the existing password
        login_response = self.client.post('/user/login/', data=dict(
            name='sam',
            password='1234'
        ), follow_redirects=True)

        #Check to ensure initial login is successful
        self.assertIn(b'Login successful', login_response.data)

        # Change the password
        change_response = self.client.post('/changepass/', data=dict(
            name='sam',
            password='1234',
            new_password=''
        ), follow_redirects=True)

        #Check to make sure password change does not occur
        self.assertIn(b'Errors occured verifying your input. Please check the marked fields below.', change_response.data)

if __name__ == '__main__':
    unittest.main()


"""
OUTPUT FROM TESTS:

/Users/Kenny/PycharmProjects/pythonProject/venv/bin/python /Applications/PyCharm.app/Contents/plugins/python/helpers/pycharm/_jb_pytest_runner.py --path /Users/Kenny/PycharmProjects/pythonProject/tests/testPassword.py 
Testing started at 9:24 PM ...
Launching pytest with arguments /Users/Kenny/PycharmProjects/pythonProject/tests/testPassword.py --no-header --no-summary -q in /Users/Kenny/PycharmProjects/pythonProject/tests

============================= test session starts ==============================
collecting ... collected 4 items

testPassword.py::PasswordTests::test_change_password_incorrect_password 
testPassword.py::PasswordTests::test_change_password_new_password_blank 
testPassword.py::PasswordTests::test_change_password_old_left_blank 
testPassword.py::PasswordTests::test_change_password_valid_credentials 

======================== 4 passed, 6 warnings in 0.56s =========================
PASSED [ 25%]PASSED [ 50%]PASSED [ 75%]PASSED [100%]
Process finished with exit code 0
"""
