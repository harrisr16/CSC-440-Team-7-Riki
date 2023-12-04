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

    def test_image_upload_and_display(self):

        with open('test_image.jpg', 'rb') as img:
            image = FileStorage(img)
            response = self.client.post('/upload_image', data={'image': image}, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)

            self.assertIn('Image uploaded successfully.', response.data.decode())


            response = self.client.get('/display_image/' + response.json['image_id'])


            self.assertEqual(response.status_code, 200)


            self.assertEqual(response.data, image.read())

if __name__ == '__main__':
    unittest.main()
