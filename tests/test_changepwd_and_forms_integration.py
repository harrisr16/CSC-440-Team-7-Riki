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

def testPassChangeAndForms(app):
    user = app.test_client()

    with user:
        responseUserLogin = user.post('/user/login/', data=dict(
            name='name',
            password='1234'
        ), follow_redirects=True)
        assert responseUserLogin.status_code == 200

        responseChangeForm = user.get('/changepass/') #Verify form is retrieved by user
        assert responseChangeForm.status_code == 200

        user.post('/changepass/', data=dict(
            name='name',
            password='1234',
            new_password='12345'
        ), follow_redirects=True)
        currUser = current_users.get_user('name') #Verify user is in the user list
        assert currUser.is_authenticated() is True
