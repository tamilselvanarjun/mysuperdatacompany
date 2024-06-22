from django.db import models

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class DataRecord(models.Model):
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    data = models.JSONField()
    type = models.CharField(max_length=50, null=True, blank=True)
