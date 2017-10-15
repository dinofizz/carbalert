# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from .tasks import send_email_notification
import maya

from carbalert_django.models import Thread, SearchPhrase


class CarbalertPipeline(object):
    def process_item(self, item, spider):
        try:
            thread = Thread.objects.get(thread_id=item["thread_id"])
            logging.info("Thread already exists.")
            return item
        except Thread.DoesNotExist:
            pass

        search_phrases = SearchPhrase.objects.values_list('phrase', flat=True)

        title = item['title']
        text = item['text']
        thread_url = item['thread_url']
        thread_datetime = maya.parse(item['datetime'])

        phrases_found = []
        phrase_hit = False

        for search_phrase in search_phrases:
            if search_phrase.lower() in title.lower() or search_phrase.lower() in text.lower():
                search_phrase_object = SearchPhrase.objects.get(phrase=search_phrase)
                new_thread = Thread()
                new_thread.thread_id = item['thread_id']
                new_thread.title = title
                new_thread.text = text
                new_thread.url = thread_url
                new_thread.datetime = thread_datetime.datetime()
                new_thread.save()
                new_thread.search_phrases.add(search_phrase_object)
                new_thread.save()
                phrase_hit = True
                phrases_found.append(search_phrase)

        if phrase_hit is True:
            local_datetime = thread_datetime.datetime(to_timezone='Africa/Harare').strftime("%d-%m-%Y %H:%M")
            send_email_notification.delay(phrases_found, title, text, thread_url, local_datetime)

        return item
