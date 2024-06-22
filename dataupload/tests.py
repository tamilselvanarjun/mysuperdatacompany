from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import UploadFileForm
import os

class UploadFileFormTest(TestCase):
    def test_form_valid_csv(self):
        file = SimpleUploadedFile("test_file.csv", b"col1,col2\nval1,val2", content_type="text/csv")
        form_data = {'file': file}
        form = UploadFileForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid_json(self):
        file = SimpleUploadedFile("test_file.json", b'{"key": "value"}', content_type="application/json")
        form_data = {'file': file}
        form = UploadFileForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_no_file(self):
        form = UploadFileForm(data={})
        self.assertFalse(form.is_valid())

    def test_form_invalid_file_type(self):
        file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
        form_data = {'file': file}
        form = UploadFileForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())

class UploadFileViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        response = self.client.get('/data/upload/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload.html')

    def test_post_request_valid_csv_file(self):
        file = SimpleUploadedFile("test_file.csv", b"col1,col2\nval1,val2", content_type="text/csv")
        response = self.client.post('/data/upload/', {'file': file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File uploaded successfully')

    def test_post_request_valid_json_file(self):
        file = SimpleUploadedFile("test_file.json", b'{"key": "value"}', content_type="application/json")
        response = self.client.post('/data/upload/', {'file': file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File uploaded successfully')

    def test_post_request_invalid_file_type(self):
        file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
        response = self.client.post('/data/upload/', {'file': file})
        self.assertEqual(response.status_code, 400)

    def test_handle_uploaded_file_csv(self):
        file = SimpleUploadedFile("test_file.csv", b"col1,col2\nval1,val2", content_type="text/csv")
        response = self.client.post('/data/upload/', {'file': file})
        file_path = os.path.join(os.getcwd(), "uploads", "test_file.csv")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b"col1,col2\nval1,val2")
        os.remove(file_path)

    def test_handle_uploaded_file_json(self):
        file = SimpleUploadedFile("test_file.json", b'{"key": "value"}', content_type="application/json")
        response = self.client.post('/data/upload/', {'file': file})
        file_path = os.path.join(os.getcwd(), "uploads", "test_file.json")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'{"key": "value"}')
        os.remove(file_path)
