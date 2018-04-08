import re

import html2text
import scrapy


class CarbSpider(scrapy.Spider):
    name = "carb"
    start_urls = [
        'https://carbonite.co.za/index.php?forums/laptops.32/',
    ]

    def parse(self, response):
        threads = response.css('.js-threadList').css('.structItem--thread')

        for thread in threads:
            item = {}
            thread_url_partial = thread.css('.structItem-cell--main').xpath(".//a").css("::attr(href)")[1].extract()
            item['title'] = thread.css('.structItem-cell--main').css('.structItem-title').xpath(
                './/a/text()').extract_first()
            item['thread_id'] = re.findall(r'\.(\d+)/', thread_url_partial)[0]
            item['thread_url'] = response.urljoin(thread_url_partial)
            request = scrapy.Request(item['thread_url'], callback=self.parse_thread)
            request.meta['item'] = item
            yield request

    def parse_thread(self, response):
        datetime = response.css('.message-main')[0].xpath('.//time').css("::attr(datetime)").extract_first()
        html = response.css('.message-main')[0].css('.bbWrapper').extract_first()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        item = response.meta['item']
        item['text'] = converter.handle(html)
        item['datetime'] = datetime
        yield item
