import scrapy
import html2text


class CarbSpider(scrapy.Spider):
    name = "carb"
    start_urls = [
        'http://carbonite.co.za/forumdisplay.php?47-Laptops',
    ]

    def parse(self, response):
        threads = response.css('ol.threads').css('li.threadbit')

        for thread in threads:
            item = {}
            thread_url_partial = thread.css('a.title::attr(href)').extract_first()
            item['title'] = thread.css('a.title::text').extract_first()
            item['thread_id'] = thread.css('li::attr(id)').extract_first()
            item['thread_url'] = response.urljoin(thread_url_partial)
            request = scrapy.Request(item['thread_url'],
                                     callback=self.parse_thread)
            request.meta['item'] = item
            yield request

    def parse_thread(self, response):
        original_post = response.css('ol.posts').css('div.content')[0]
        item = response.meta['item']
        html = original_post.css('blockquote').extract_first()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        item['text'] = converter.handle(html)

        yield item
