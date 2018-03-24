import logging

import html2text
import maya
import scrapy


class CarbSpider(scrapy.Spider):
    name = "carb"
    start_urls = [
        'http://xenforo2.carbonite.co.za/index.php?forums/laptops.32/',
    ]

    def parse(self, response):
        threads = response.css('.js-threadList').css('.structItem--thread')
        # threads = response.css('ol.threads').css('li.threadbit')

        for thread in threads:
            item = {}
            thread_url_partial = thread.css('.structItem-cell--main').xpath(".//a").css("::attr(href)")[1].extract()
            # redo fromi here
            item['title'] = thread.css('a.title::text').extract_first()
            item['thread_id'] = thread.css('li::attr(id)').extract_first()
            item['thread_url'] = response.urljoin(thread_url_partial)
            request = scrapy.Request(item['thread_url'], callback=self.parse_thread)
            request.meta['item'] = item
            yield request

    def parse_thread(self, response):
        original_post_datetime = response.css('ol.posts').css('li.postbit')[0]
        op_date = original_post_datetime.css('span.date::text').extract_first().replace(",\xa0", "")

        if op_date == "Today" or op_date == "Yesterday":
            op_date = maya.when(op_date).datetime().strftime("%d-%m-%Y")

        op_time = original_post_datetime.css('span.date').css('span.time::text').extract_first()
        op_datetime = f"{op_date} {op_time}"
        datetime = maya.when(op_datetime, timezone="Africa/Harare").iso8601()
        original_post = response.css('ol.posts').css('div.content')[0]
        item = response.meta['item']
        html = original_post.css('blockquote').extract_first()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        item['text'] = converter.handle(html)
        item['datetime'] = datetime
        yield item
