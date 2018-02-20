# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import maya

# The path for this is weird. I spent some time trying to get it to work with the a more sane import statement
# but I was not (yet) successful.
from carbalert_django.models import Thread, SearchPhrase
from .tasks import send_email_notification


class CarbalertPipeline(object):
    def process_item(self, item, spider):
        thread_id = item['thread_id']

        if Thread.objects.filter(thread_id=thread_id).exists():
            logging.debug("Thread already exists.")
            return item

        search_phrases = SearchPhrase.objects.values_list('phrase', flat=True)

        title = item['title']
        text = item['text']
        thread_url = item['thread_url']
        thread_datetime = maya.parse(item['datetime'])

        email_list = {}

        for search_phrase in search_phrases:
            if search_phrase.lower() in title.lower() or search_phrase.lower() in text.lower():
                search_phrase_object = SearchPhrase.objects.get(phrase=search_phrase)

                for user in search_phrase_object.email_users.all():
                    if user in email_list:
                        phrase_hits_for_user = email_list[user]
                        phrase_hits_for_user.append(search_phrase)
                    else:
                        email_list[user] = [search_phrase]

                try:
                    thread = Thread.objects.get(thread_id=thread_id)
                except Thread.DoesNotExist:
                    thread = Thread()
                    thread.thread_id = thread_id
                    thread.title = title
                    thread.text = text
                    thread.url = thread_url
                    thread.datetime = thread_datetime.datetime()
                    thread.save()

                thread.search_phrases.add(search_phrase_object)
                thread.save()

        local_datetime = thread_datetime.datetime(to_timezone='Africa/Harare').strftime("%d-%m-%Y %H:%M")

        for user in email_list:
            send_email_notification.delay(user.email, email_list[user], title, text, thread_url, local_datetime)

        return item
