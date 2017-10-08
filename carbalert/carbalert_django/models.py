from django.db import models


class Thread(models.Model):
    thread_id = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=200, blank=True)
    text = models.CharField(max_length=1000)
    datetime = models.DateTimeField(blank=True)
