# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import maya

from carbalert_django.models import Thread, SearchPhrase


class CarbalertPipeline(object):
    def process_item(self, item, spider):
        logging.info(item['title'])

        try:
            thread = Thread.objects.get(thread_id=item["thread_id"])
            logging.info("Thread already exists.")
            return item
        except Thread.DoesNotExist:
            pass

        search_phrases = SearchPhrase.objects.values_list('phrase', flat=True)

        for search_phrase in search_phrases:
            if search_phrase.lower() in item['title'].lower() or search_phrase in item['text'].lower():
                search_phrase_object = SearchPhrase.objects.get(phrase=search_phrase)
                new_thread = Thread()
                new_thread.thread_id = item['thread_id']
                new_thread.title = item['title']
                new_thread.text = item['text']
                new_thread.url = item['thread_url']
                new_thread.datetime = maya.parse(item['datetime']).datetime()
                new_thread.save()
                new_thread.search_phrases.add(search_phrase_object)
                new_thread.save()

        return item
