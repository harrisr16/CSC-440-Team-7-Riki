import pytest
import os
from wiki import create_app
from wiki.web import current_users

@pytest.fixture
def app():
    dir = os.getcwd()
    app = create_app(dir)

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

def testRegistrationAndForms(app):
    user = app.test_client()

    with user:
        responseRegisterForm = user.get('/register/') #Verify form is retrieved by user
        user.post('/register/', data={
            'username': 'newGuy',
            'password': '123',
            'confirm_password': '123'
        })
        currUser = current_users.get_user('newGuy') #Verify user is in the user list

        assert responseRegisterForm.status_code == 200
        assert currUser.is_authenticated() is True
