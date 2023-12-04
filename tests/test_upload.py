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
        # Open an image file in binary mode
        with open('test_image.jpg', 'rb') as img:
            # Create a FileStorage object from the image file
            image = FileStorage(img)

            # Send a POST request to the '/upload_image' route with the image
            response = self.client.post('/upload_image', data={'image': image}, content_type='multipart/form-data')

            # Check that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

            # Check that the response data contains the success message
            self.assertIn('Image uploaded successfully.', response.data.decode())

            # Send a GET request to the '/display_image' route with the image ID
            response = self.client.get('/display_image/' + response.json['image_id'])

            # Check that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)

            # Check that the response data contains the image data
            self.assertEqual(response.data, image.read())

if __name__ == '__main__':
    unittest.main()
