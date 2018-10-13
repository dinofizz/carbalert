import logging
import re

import html2text
import scrapy


class CarbSpider(scrapy.Spider):
    name = "carb"
    start_urls = ["https://carbonite.co.za/index.php?forums/laptops.32/"]

    def parse(self, response):
        logging.info("CarbSpider: Parsing response")
        threads = response.css(".js-threadList").css(".structItem--thread")

        logging.info(f"Found {len(threads)} threads.")

        for thread in threads:
            item = {}

            thread_url_partial = (
                thread.css(".structItem-cell--main")
                .xpath(".//a")
                .css("::attr(href)")[1]
                .extract()
            )
            thread_url = response.urljoin(thread_url_partial)
            logging.info(f"Thread URL: {thread_url}")
            item["thread_url"] = thread_url

            thread_title = (
                thread.css(".structItem-cell--main")
                .css(".structItem-title")
                .xpath(".//a/text()")
                .extract_first()
            )
            logging.info(f"Thread title: {thread_title}")
            item["title"] = thread_title

            thread_id = re.findall(r"\.(\d+)/", thread_url_partial)[0]
            item["thread_id"] = thread_id
            logging.info(f"Thread ID: {thread_id}")

            request = scrapy.Request(item["thread_url"], callback=self.parse_thread)
            request.meta["item"] = item
            yield request

    def parse_thread(self, response):
        item = response.meta["item"]

        thread_timestamp = (
            response.css(".message-main")[0]
            .xpath(".//time")
            .css("::attr(datetime)")
            .extract_first()
        )
        logging.info(f"Thread timestamp: {thread_timestamp}")
        item["datetime"] = thread_timestamp

        html = response.css(".message-main")[0].css(".bbWrapper").extract_first()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        thread_text = converter.handle(html)
        logging.info(f"Thread text: {thread_text}")
        item["text"] = thread_text

        yield item
