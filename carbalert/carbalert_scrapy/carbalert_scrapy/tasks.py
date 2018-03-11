import requests
from celery import Celery, bootsteps, Task, shared_task
from celery.bin import Option
from celery.utils.log import get_task_logger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from carbalert.carbalert_scrapy.carbalert_scrapy.spiders.carb_spider import CarbSpider


class APITask(Task):
    """API requests task class."""

    abstract = True

    mailgun_api_key = None
    mailgun_email = None
    mailgun_domain = None


class MailgunArgs(bootsteps.Step):

    def __init__(self, worker, mailgun_domain, mailgun_email, mailgun_api_key, **options):
        APITask.mailgun_domain = mailgun_domain[0]
        APITask.mailgun_email = mailgun_email[0]
        APITask.mailgun_api_key = mailgun_api_key[0]


logger = get_task_logger(__name__)
app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'
app.user_options['worker'].add(
    Option('--domain', dest='mailgun_domain', default=None, help='Mailgun domain')
)

app.user_options['worker'].add(
    Option('--email', dest='mailgun_email', default=None, help='Mailgun "from" email address.')
)

app.user_options['worker'].add(
    Option('--key', dest='mailgun_api_key', default=None, help='Mailgun API key')
)

app.steps['worker'].add(MailgunArgs)

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


@shared_task(base=APITask, bind=True)
def send_email_notification(self, email_address, phrases, title, text, thread_url, thread_datetime):
    logger.info(f"Received alert for {email_address} for thread title: {title}")
    subject = f"CARBALERT: {title}"

    phrase_list = ""

    for phrase in phrases:
        phrase_list += f"{phrase}\n"

    text = f"{phrase_list}\n{thread_datetime}\n\n{title}\n\n{text}\n\n{thread_url}\n\nEND\n"

    mailgun_url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
    mailgun_from = f"CarbAlert <{self.mailgun_email}>"

    try:
        response = requests.post(
            mailgun_url,
            auth=("api", self.mailgun_api_key),
            data={"from": mailgun_from,
                  "to": [email_address],
                  "subject": subject,
                  "text": text})
        if response.status_code is not 200:
            logger.error(f"Unexpected error code received on Mailgun response. "
                         f"Code: {response.status_code}, Raw {response.raw}")
    except Exception as ex:
        logger.error(f"Error sending mail: {ex}")
