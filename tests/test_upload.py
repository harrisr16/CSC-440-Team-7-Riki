import os
import unittest
from flask import Flask
from werkzeug.datastructures import FileStorage
from Riki import create_app

class UploadTest(unittest.TestCase):
    def create_app(self):
        directory = os.getcwd()
        app = create_app(directory)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()

    def test_upload(self):
        with open('test_file.txt', 'w') as f:
            f.write('This is a test file.')

        with open('test_file.txt', 'rb') as f:
            data = {
                'file': (f, 'test_file.txt'),
            }
            response = self.client.post('/upload', content_type='multipart/form-data', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('File was uploaded.', response.data.decode())

if __name__ == '__main__':
    unittest.main()
