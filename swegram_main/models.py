from __future__ import unicode_literals

from django.db import models

# This is used to check if an uploaded file has previously been annotated,
# if the md5 matches we can determine whether it's been normalized or not

class UploadedFile(models.Model):
    md5_checksum = models.CharField(max_length=32, blank=False, primary_key=True)
    normalized = models.BooleanField(blank=False)
