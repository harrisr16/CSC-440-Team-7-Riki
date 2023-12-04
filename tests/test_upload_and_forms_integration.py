import pytest
import os
from wiki import create_app

@pytest.fixture
def app():
    dir = os.getcwd()
    app = create_app(dir)

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

def testUploadAndForms(app):
    user = app.test_client()

    with user:
        responseUserLogin = user.post('/user/login/', data=dict(
            name='name',
            password='1234'
        ), follow_redirects=True)
        assert responseUserLogin.status_code == 200

        responseUserEdit = user.get('/edit/home/')
        assert responseUserEdit.status_code == 302
