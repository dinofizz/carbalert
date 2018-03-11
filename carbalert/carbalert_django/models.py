from django.contrib.auth.models import User
from django.db import models


class SearchPhrase(models.Model):
    phrase = models.CharField(max_length=100, blank=True)
    email_users = models.ManyToManyField(User, related_name='email_users')

    def __str__(self):
        return self.phrase


class Thread(models.Model):
    thread_id = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=200, blank=True)
    text = models.TextField(max_length=1000)
    datetime = models.DateTimeField(blank=True)
    search_phrases = models.ManyToManyField(SearchPhrase)

    def __str__(self):
        return self.title
