import requests
from celery import Celery, bootsteps
from celery.utils.log import get_task_logger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from carbalert.carbalert_scrapy.carbalert_scrapy.spiders.carb_spider import CarbSpider


def add_worker_arguments(parser):
    parser.add_argument(
        '--domain', default=False,
        help='Mailgun domain',
    ),
    parser.add_argument(
        '--email', default=False,
        help='Mailgun from email address',
    ),
    parser.add_argument(
        '--key', default=False,
        help='Mailgun API key',
    ),


class MailgunDomain(bootsteps.Step):

    def __init__(self, worker, domain, **options):
        if domain:
            worker.app.mailgun_domain = domain


class MailgunFromAddress(bootsteps.Step):

    def __init__(self, worker, email, **options):
        if email:
            worker.app.mailgun_from_address = email


class MailgunApiKey(bootsteps.Step):

    def __init__(self, worker, key, **options):
        if key:
            worker.app.mailgun_api_key = key


logger = get_task_logger(__name__)
app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'
app.user_options['worker'].add(add_worker_arguments)
app.steps['worker'].add(MailgunDomain)
app.steps['worker'].add(MailgunFromAddress)
app.steps['worker'].add(MailgunApiKey)

app.conf.beat_schedule = {
    'add-every-300-seconds': {
        'task': 'carbalert_scrapy.tasks.scrape_carbonite',
        'schedule': 300.0
    },
}


@app.task
def scrape_carbonite():
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(CarbSpider)
    process.start()


@app.task
def send_email_notification(email_address, phrases, title, text, thread_url, thread_datetime):
    logger.info(f"Received alert for {email_address} for thread title: {title}")
    subject = f"CARBALERT: {title}"

    phrase_list = ""

    for phrase in phrases:
        phrase_list += f"{phrase}\n"

    text = f"{phrase_list}\n{thread_datetime}\n\n{title}\n\n{text}\n\n{thread_url}\n\nEND\n"

    mailgun_url = f"https://api.mailgun.net/v3/{app.mailgun_domain}/messages"
    mailgun_from = f"CarbAlert <{app.mailgun_from_address}>"

    try:
        requests.post(
            mailgun_url,
            auth=("api", app.mailgun_api_key),
            data={"from": mailgun_from,
                  "to": [email_address],
                  "subject": subject,
                  "text": text})
    except Exception as ex:
        logger.error(f"Error sending mail: {ex}")
